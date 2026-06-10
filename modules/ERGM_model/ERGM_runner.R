suppressMessages({
  library(ergm)
  library(network)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
n              <- as.integer(args[1])
edges_coef     <- as.numeric(args[2])
triangles_coef <- as.numeric(args[3])
n_samples      <- as.integer(args[4])
seed           <- as.integer(args[5])

if (!is.na(seed)) set.seed(seed)

# Build empty base network
net <- network.initialize(n, directed = FALSE)

# ergm 4 syntax — pass formula and coef directly to simulate
simulated <- simulate(
  net ~ edges + triangles,
  coef    = c(edges_coef, triangles_coef),
  nsim    = 1,
  control = control.simulate(
    MCMC.burnin   = 1000,
    MCMC.interval = 100
  )
)

# Convert to edge list
el <- as.edgelist(simulated)

if (is.null(el) || nrow(el) == 0) {
  edges_out <- list()
} else {
  edges_out <- lapply(1:nrow(el), function(i) {
    list(source = el[i, 1] - 1L, target = el[i, 2] - 1L)
  })
}

nodes_out <- lapply(0:(n - 1), function(i) list(id = i))

output <- list(
  nodes    = nodes_out,
  edges    = edges_out,
  metadata = list(
    model      = "ergm",
    n_nodes    = n,
    n_edges    = length(edges_out),
    directed   = FALSE,
    parameters = list(
      edges_coef     = edges_coef,
      triangles_coef = triangles_coef
    )
  )
)

cat(toJSON(output, auto_unbox = TRUE))
