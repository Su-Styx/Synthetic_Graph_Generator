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

      simulated <- simulate(
        fit,
        nsim = 1,
        control = control.simulate.ergm(
          MCMC.burnin = 20000,
          MCMC.interval = 1000
        )
      )

      list(fit = fit, simulated = simulated, label = label)
    }, error = function(e) {
      cat(sprintf("Spec failed: %s -> %s\n", label, conditionMessage(e)), file = log_con)
      NULL
    })

    if (!is.null(fit_result)) {
      cat(sprintf("Spec succeeded: %s\n", label), file = log_con)
      return(fit_result)
    }
  }

  stop("All ERGM specifications failed or degenerated")
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
      coefficients = as.list(coef(fit))
    )
  )
}, error = function(e) {
  cat(sprintf("ERGM runner failed: %s\n", conditionMessage(e)), file = log_con)
  quit(status = 1)
})

sink(type = "message")
cat(toJSON(result, auto_unbox = TRUE))