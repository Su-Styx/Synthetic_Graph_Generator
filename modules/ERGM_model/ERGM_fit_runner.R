suppressMessages({
  library(ergm)
  library(network)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
file_path <- args[1]
seed_arg  <- if (length(args) >= 2) args[2] else "NA"
directed_arg <- if (length(args) >= 3) args[3] else "AUTO"

if (is.null(file_path) || is.na(file_path) || file_path == "") {
  stop("No input file path provided")
}

if (!is.na(seed_arg) && seed_arg != "NA") {
  set.seed(as.integer(seed_arg))
}

parse_bool <- function(x) {
  if (is.null(x) || is.na(x)) return(NA)
  x <- toupper(trimws(as.character(x)))
  if (x %in% c("TRUE", "T", "1", "YES")) return(TRUE)
  if (x %in% c("FALSE", "F", "0", "NO")) return(FALSE)
  NA
}

read_edge_file <- function(path, max_lines = NULL) {
  lines <- readLines(path, warn = FALSE)
  lines <- trimws(lines)
  lines <- lines[lines != ""]

  is_mtx <- grepl("\\.mtx$", path, ignore.case = TRUE)

  if (is_mtx) {
    lines <- lines[!startsWith(lines, "%")]
    if (length(lines) < 2) {
      stop("MatrixMarket file has no data rows after removing header")
    }
    lines <- lines[-1]
  } else {
    lines <- lines[!startsWith(lines, "#")]
  }

  if (length(lines) == 0) {
    stop("Input edge file is empty")
  }

  if (!is.null(max_lines) && length(lines) > max_lines) {
    lines <- lines[1:max_lines]
  }

  first_line <- lines[1]

  if (grepl(",", first_line, fixed = TRUE)) {
    df <- read.csv(text = paste(lines, collapse = "\n"), header = FALSE, stringsAsFactors = FALSE)
  } else {
    df <- read.table(text = paste(lines, collapse = "\n"), header = FALSE, stringsAsFactors = FALSE)
  }

  if (ncol(df) < 2) {
    stop("Edge file must contain at least two columns")
  }

  df <- df[, 1:2]
  names(df) <- c("source", "target")

  df$source <- trimws(as.character(df$source))
  df$target <- trimws(as.character(df$target))

  df <- df[df$source != "" & df$target != "", , drop = FALSE]
  df <- df[df$source != df$target, , drop = FALSE]

  if (nrow(df) == 0) {
    stop("No usable edges found after cleaning")
  }

  df
}

infer_directed <- function(path, edges_df, directed_arg = "AUTO") {
  explicit <- parse_bool(directed_arg)
  if (!is.na(explicit)) {
    return(list(directed = explicit, method = "explicit"))
  }

  is_mtx <- grepl("\\.mtx$", path, ignore.case = TRUE)
  if (is_mtx) {
    return(list(directed = FALSE, method = "mtx-default-undirected"))
  }

  edge_keys <- paste(edges_df$source, edges_df$target, sep = "|||")
  reverse_keys <- paste(edges_df$target, edges_df$source, sep = "|||")
  mutual_fraction <- mean(reverse_keys %in% edge_keys)
  if (is.na(mutual_fraction)) mutual_fraction <- 0

  if (mutual_fraction > 0.2) {
    return(list(directed = TRUE, method = sprintf("heuristic-mutual=%.4f", mutual_fraction)))
  }

  return(list(directed = FALSE, method = sprintf("heuristic-undirected-mutual=%.4f", mutual_fraction)))
}

dedupe_edges <- function(edges_df, directed = FALSE) {
  if (directed) {
    edges_df <- unique(edges_df[, c("source", "target")])
  } else {
    a <- pmin(edges_df$source, edges_df$target)
    b <- pmax(edges_df$source, edges_df$target)
    edges_df <- unique(data.frame(source = a, target = b, stringsAsFactors = FALSE))
  }
  edges_df
}

# Converts a fitted `ergm` object's coefficient table into a JSON-friendly
# list, including standard errors and p-values (not just point estimates).
extract_coef_table <- function(fit) {
  s <- summary(fit)
  coef_mat <- tryCatch(s$coefficients, error = function(e) NULL)

  if (is.null(coef_mat)) {
    # Fall back to plain coefficients if summary structure differs
    return(lapply(names(coef(fit)), function(nm) {
      list(term = nm, estimate = unname(coef(fit)[nm]))
    }))
  }

  term_names <- rownames(coef_mat)
  lapply(seq_along(term_names), function(i) {
    row <- coef_mat[i, ]
    list(
      term = term_names[i],
      estimate = unname(row[["Estimate"]]),
      std_error = unname(row[["Std. Error"]]),
      p_value = unname(row[[grep("Pr", names(row), value = TRUE)[1]]])
    )
  })
}

# Basic convergence / degeneracy check. A fit that "succeeded" numerically
# can still be unreliable if the MLE didn't actually converge, or if
# standard errors are NA/Inf (a classic sign of near-degeneracy).
check_convergence <- function(fit) {
  se <- tryCatch(summary(fit)$coefficients[, "Std. Error"], error = function(e) NA)
  has_bad_se <- any(is.na(se)) || any(!is.finite(se))

  failure_flag <- isTRUE(fit$failure)

  list(
    converged = !failure_flag && !has_bad_se,
    failure_flag = failure_flag,
    has_bad_std_errors = has_bad_se
  )
}

# Runs ergm::gof() on the fitted model using the statnet-recommended
# out-of-model statistics (degree/espartners/distance, split into
# idegree/odegree for directed networks) plus `model` to directly test
# the in-model terms, then converts the resulting tables into a
# JSON-friendly nested list. See:
# https://statnet.org/workshop-ergm/ergm_tutorial.html#6_Examining_the_quality_of_model_fit_%E2%80%94_GOF
run_gof <- function(fit, directed, log_con, nsim = 100) {
  gof_formula <- if (directed) {
    ~ idegree + odegree + espartners + distance + model
  } else {
    ~ degree + espartners + distance + model
  }

  cat("Running GOF diagnostics...\n", file = log_con)

  gof_obj <- tryCatch({
    gof(
      fit,
      GOF = gof_formula,
      control = control.gof.ergm(
        nsim = nsim,
        MCMC.burnin = 20000,
        MCMC.interval = 1000
      )
    )
  }, error = function(e) {
    cat(sprintf("GOF computation failed: %s\n", conditionMessage(e)), file = log_con)
    NULL
  })

  if (is.null(gof_obj)) {
    return(NULL)
  }

  # gof() returns a list of matrices/data.frames, one per statistic
  # (e.g. $degree, $espartners, $distance, $model). Convert each into a
  # list of per-bin records: {stat, obs, min, mean, max, mc_p_value, ...}
  out <- list()
  for (nm in names(gof_obj)) {
    val <- gof_obj[[nm]]
    if (is.matrix(val) || is.data.frame(val)) {
      df <- as.data.frame(val)
      colnames(df) <- make.names(colnames(df), unique = TRUE)
      rn <- rownames(df)

      records <- lapply(seq_len(nrow(df)), function(i) {
        rec <- as.list(df[i, , drop = TRUE])
        rec$stat_level <- rn[i]
        rec
      })

      if (length(records) > 0) {
        out[[nm]] <- records
      }
    }
  }

  cat("GOF diagnostics complete.\n", file = log_con)
  out
}

fit_and_simulate <- function(net, formulas, log_con) {
  last_error <- NULL

  for (spec in formulas) {
    label <- spec$label
    formula_obj <- spec$formula

    cat(sprintf("Trying ERGM spec: %s\n", label), file = log_con)

    fit_result <- tryCatch({
      fit <- ergm(
        formula_obj,
        control = control.ergm(
          MCMLE.maxit = 12,
          MCMC.interval = 4096,
          MCMC.burnin = 16384
        )
      )

      convergence <- check_convergence(fit)
      if (!convergence$converged) {
        stop(sprintf(
          "Fit did not converge cleanly (failure_flag=%s, bad_std_errors=%s)",
          convergence$failure_flag, convergence$has_bad_std_errors
        ))
      }

      simulated <- simulate(
        fit,
        nsim = 1,
        control = control.simulate.ergm(
          MCMC.burnin = 20000,
          MCMC.interval = 1000
        )
      )

      list(fit = fit, simulated = simulated, label = label, convergence = convergence)
    }, error = function(e) {
      cat(sprintf("Spec failed: %s -> %s\n", label, conditionMessage(e)), file = log_con)
      NULL
    })

    if (!is.null(fit_result)) {
      cat(sprintf("Spec succeeded: %s\n", label), file = log_con)
      return(fit_result)
    }
  }

  stop("All ERGM specifications failed, degenerated, or did not converge")
}

log_con <- stderr()
sink(log_con, type = "message")

result <- tryCatch({
  cat(sprintf("Loading graph from: %s\n", file_path), file = stderr())

  edges_df <- read_edge_file(file_path)
  cat(sprintf("Loaded %d raw edges\n", nrow(edges_df)), file = log_con)

  direction_info <- infer_directed(file_path, edges_df, directed_arg)
  directed_flag <- direction_info$directed
  cat(sprintf("Directed inference: %s (%s)\n", directed_flag, direction_info$method), file = log_con)

  edges_df <- dedupe_edges(edges_df, directed = directed_flag)
  cat(sprintf("Edges after deduplication: %d\n", nrow(edges_df)), file = log_con)

  all_nodes <- sort(unique(c(edges_df$source, edges_df$target)))
  if (length(all_nodes) < 2) {
    stop("Need at least 2 distinct nodes to fit ERGM")
  }

  cat(sprintf("Loaded %d nodes\n", length(all_nodes)), file = log_con)

  node_map <- setNames(seq_along(all_nodes), all_nodes)
  el_matrix <- as.matrix(edges_df[, c("source", "target")])
  storage.mode(el_matrix) <- "character"

  mapped <- node_map[el_matrix]
  if (anyNA(mapped)) {
    bad_vals <- unique(el_matrix[is.na(mapped)])
    stop(
      paste(
        "Node remapping produced NA values. Unmapped examples:",
        paste(head(bad_vals, 10), collapse = ", ")
      )
    )
  }

  el_matrix <- matrix(as.integer(mapped), ncol = 2, byrow = FALSE)
  if (nrow(el_matrix) == 0 || ncol(el_matrix) != 2) {
    stop("Edge matrix is malformed after remapping")
  }

  net <- network(el_matrix, directed = directed_flag, matrix.type = "edgelist")
  network.vertex.names(net) <- all_nodes

  cat("Preparing ERGM specifications...\n", file = log_con)

  if (directed_flag) {
    formulas <- list(
      list(label = "edges + mutual + gwesp + gwidegree + gwodegree",
           formula = net ~ edges + mutual + gwesp(0.25, fixed = TRUE) + gwidegree(0.5, fixed = TRUE) + gwodegree(0.5, fixed = TRUE)),
      list(label = "edges + mutual + gwesp",
           formula = net ~ edges + mutual + gwesp(0.25, fixed = TRUE)),
      list(label = "edges + gwidegree + gwodegree",
           formula = net ~ edges + gwidegree(0.5, fixed = TRUE) + gwodegree(0.5, fixed = TRUE)),
      list(label = "edges",
           formula = net ~ edges)
    )
  } else {
    formulas <- list(
      list(label = "edges + gwesp + gwdegree",
           formula = net ~ edges + gwesp(0.25, fixed = TRUE) + gwdegree(0.5, fixed = TRUE)),
      list(label = "edges + gwdegree",
           formula = net ~ edges + gwdegree(0.5, fixed = TRUE)),
      list(label = "edges + gwesp",
           formula = net ~ edges + gwesp(0.25, fixed = TRUE)),
      list(label = "edges",
           formula = net ~ edges)
    )
  }

  fit_result <- fit_and_simulate(net, formulas, log_con)

  fit <- fit_result$fit
  simulated <- fit_result$simulated
  chosen_spec <- fit_result$label
  convergence <- fit_result$convergence

  gof_results <- run_gof(fit, directed_flag, log_con, nsim = 100)

  el <- as.edgelist(simulated)
  vertex_names <- network.vertex.names(simulated)

  if (is.null(el) || nrow(el) == 0) {
    edges_out <- list()
  } else {
    edges_out <- lapply(seq_len(nrow(el)), function(i) {
      list(
        source = as.character(vertex_names[el[i, 1]]),
        target = as.character(vertex_names[el[i, 2]])
      )
    })
  }

  nodes_out <- lapply(vertex_names, function(v) {
    list(id = as.character(v))
  })

  model_summary <- summary(fit)

  list(
    nodes = nodes_out,
    edges = edges_out,
    metadata = list(
      model = "ergm",
      fitted = TRUE,
      source_file = file_path,
      directed = directed_flag,
      directed_inference_method = direction_info$method,
      chosen_spec = chosen_spec,
      observed_n_nodes = network.size(net),
      observed_n_edges = network.edgecount(net),
      generated_n_nodes = length(nodes_out),
      generated_n_edges = length(edges_out),
      coefficients = as.list(coef(fit)),
      coefficient_table = extract_coef_table(fit),
      convergence = convergence,
      aic = tryCatch(model_summary$aic, error = function(e) NA),
      bic = tryCatch(model_summary$bic, error = function(e) NA),
      null_deviance = tryCatch(model_summary$devtable["Model", "Deviance"], error = function(e) NA),
      gof = gof_results
    )
  )
}, error = function(e) {
  cat(sprintf("ERGM runner failed: %s\n", conditionMessage(e)), file = log_con)
  quit(status = 1)
})

sink(type = "message")
cat(toJSON(result, auto_unbox = TRUE, na = "null"))
sink(type = "message")

output_path <- if (length(args) >= 4) args[4] else paste0(file_path, ".result.json")
write(toJSON(result, auto_unbox = TRUE, na = "null"), file = output_path)
cat(output_path)  # still print the path to stdout so Python knows where to look