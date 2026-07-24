suppressMessages({
  library(ergm)
  library(network)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
file_path <- args[1]
seed_arg  <- args[2]

if (!is.na(seed_arg) && seed_arg != "NA") {
  set.seed(as.integer(seed_arg))
}

read_edge_file <- function(path) {
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

  first_line <- lines[1]

  if (grepl(",", first_line, fixed = TRUE)) {
    df <- read.csv(text = lines, header = FALSE, stringsAsFactors = FALSE)
  } else {
    df <- read.table(text = lines, header = FALSE, stringsAsFactors = FALSE)
  }

  if (ncol(df) < 2) {
    stop("Edge file must contain at least two columns")
  }

  df <- df[, 1:2]
  names(df) <- c("source", "target")
  df
}

edges_df <- read_edge_file(file_path)

all_nodes <- sort(unique(c(edges_df$source, edges_df$target)))
node_map <- setNames(seq_along(all_nodes), all_nodes)

net <- network.initialize(length(all_nodes), directed = FALSE)
network.vertex.names(net) <- as.character(all_nodes)

el_matrix <- as.matrix(edges_df[, c("source", "target")])
el_matrix[] <- node_map[el_matrix]
el_matrix <- matrix(as.integer(el_matrix), ncol = 2)

net <- network(el_matrix, directed = FALSE, matrix.type = "edgelist")
network.vertex.names(net) <- as.character(all_nodes)

fit <- ergm(net ~ edges + gwesp(0.25, fixed = TRUE))

simulated <- simulate(
  fit,
  nsim = 1,
  control = control.simulate.ergm(
    MCMC.burnin = 1000,
    MCMC.interval = 100
  )
)

el <- as.edgelist(simulated)
vertex_names <- network.vertex.names(simulated)

if (is.null(el) || nrow(el) == 0) {
  edges_out <- list()
} else {
  edges_out <- lapply(seq_len(nrow(el)), function(i) {
    list(
      source = vertex_names[el[i, 1]],
      target = vertex_names[el[i, 2]]
    )
  })
}

nodes_out <- lapply(vertex_names, function(v) list(id = v))

output <- list(
  nodes = nodes_out,
  edges = edges_out,
  metadata = list(
    model = "ergm",
    fitted = TRUE,
    source_file = file_path,
    observed_n_nodes = network.size(net),
    observed_n_edges = network.edgecount(net),
    generated_n_nodes = length(nodes_out),
    generated_n_edges = length(edges_out),
    coefficients = as.list(coef(fit))
  )
)

cat(toJSON(output, auto_unbox = TRUE))