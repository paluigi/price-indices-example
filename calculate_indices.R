#!/usr/bin/env Rscript

# Bilateral Price Index Calculator
# Uses the PriceIndices R package (https://cran.r-project.org/web/packages/PriceIndices/index.html)

if (!requireNamespace("PriceIndices", quietly = TRUE)) {
  install.packages("PriceIndices", repos = "https://cloud.r-project.org")
}

library(PriceIndices)

if (!requireNamespace("microbenchmark", quietly = TRUE)) {
  install.packages("microbenchmark", repos = "https://cloud.r-project.org")
}

library(microbenchmark)

# --------------------------------------------------------------------------
# Reusable function to calculate all bilateral indices on a dataset
# --------------------------------------------------------------------------
calculate_all_indices <- function(data, start_period, end_period) {

  start_prods <- unique(data$prodID[substr(as.character(data$time), 1, 7) == start_period])
  end_prods   <- unique(data$prodID[substr(as.character(data$time), 1, 7) == end_period])
  num_products <- length(intersect(start_prods, end_prods))

  timed_index <- function(name, expr) {
    expr_q <- substitute(expr)
    val <- eval(expr_q)
    mb <- microbenchmark(eval(expr_q), times = 10L)
    list(
      index_name   = name,
      value        = as.numeric(val),
      time_seconds = median(mb$time) / 1e9
    )
  }

  unweighted <- list(
    timed_index("Jevons",   jevons(data, start = start_period, end = end_period)),
    timed_index("Carli",    carli(data, start = start_period, end = end_period)),
    timed_index("Dutot",    dutot(data, start = start_period, end = end_period)),
    timed_index("Harmonic", harmonic(data, start = start_period, end = end_period)),
    timed_index("BMW",      bmw(data, start = start_period, end = end_period)),
    timed_index("CSWD",     cswd(data, start = start_period, end = end_period)),
    timed_index("Dikhanov", dikhanov(data, start = start_period, end = end_period)),
    timed_index("YBMD",     ybmd(data, start = start_period, end = end_period))
  )

  weighted <- list(
    timed_index("Fisher",             fisher(data, start = start_period, end = end_period)),
    timed_index("Laspeyres",          laspeyres(data, start = start_period, end = end_period)),
    timed_index("Paasche",            paasche(data, start = start_period, end = end_period)),
    timed_index("Tornqvist",          tornqvist(data, start = start_period, end = end_period)),
    timed_index("Walsh",              walsh(data, start = start_period, end = end_period)),
    timed_index("Sato_Vartia",        sato_vartia(data, start = start_period, end = end_period)),
    timed_index("Marshall_Edgeworth", marshall_edgeworth(data, start = start_period, end = end_period)),
    timed_index("Lloyd_Moulton",      lloyd_moulton(data, start = start_period, end = end_period, sigma = 0.9)),
    timed_index("Drobisch",           drobisch(data, start = start_period, end = end_period)),
    timed_index("Stuvel",             stuvel(data, start = start_period, end = end_period)),
    timed_index("Geo_Laspeyres",      geolaspeyres(data, start = start_period, end = end_period)),
    timed_index("Geo_Paasche",        geopaasche(data, start = start_period, end = end_period)),
    timed_index("Geo_Walsh",          geowalsh(data, start = start_period, end = end_period)),
    timed_index("Bialek",             bialek(data, start = start_period, end = end_period)),
    timed_index("Palgrave",           palgrave(data, start = start_period, end = end_period)),
    timed_index("AG_Mean",            agmean(data, start = start_period, end = end_period)),
    timed_index("Banajree",           banajree(data, start = start_period, end = end_period)),
    timed_index("Davies",             davies(data, start = start_period, end = end_period)),
    timed_index("Lehr",               lehr(data, start = start_period, end = end_period)),
    timed_index("Vartia",             vartia(data, start = start_period, end = end_period)),
    timed_index("Theil_I",            theil1(data, start = start_period, end = end_period)),
    timed_index("Theil_II",           theil2(data, start = start_period, end = end_period)),
    timed_index("Geo_Lowe",           geolowe(data, start = start_period, end = end_period)),
    timed_index("Geo_Young",          geoyoung(data, start = start_period, end = end_period)),
    timed_index("Geo_Hybrid",         geohybrid(data, start = start_period, end = end_period)),
    timed_index("Hybrid",             hybrid(data, start = start_period, end = end_period)),
    timed_index("HLC",                hlc(data, start = start_period, end = end_period)),
    timed_index("Walsh_Vartia",       walsh_vartia(data, start = start_period, end = end_period)),
    timed_index("Value_Index",        value_index(data, start = start_period, end = end_period)),
    timed_index("Unit_Value_Index",   unit_value_index(data, start = start_period, end = end_period))
  )

  all <- c(unweighted, weighted)
  results <- data.frame(
    index_name   = sapply(all, `[[`, "index_name"),
    value        = sprintf("%.7f", sapply(all, `[[`, "value")),
    time_seconds = sprintf("%.4f", sapply(all, `[[`, "time_seconds")),
    num_products = num_products,
    stringsAsFactors = FALSE
  )
  results
}

# --------------------------------------------------------------------------
# Dataset configurations
# --------------------------------------------------------------------------
configs <- data.frame(
  dataset      = c("performance_price_data.csv"),
  start_period = c("2024-01"),
  end_period   = c("2024-02"),
  stringsAsFactors = FALSE
)

all_results <- do.call(rbind, lapply(seq_len(nrow(configs)), function(i) {
  cfg <- configs[i, ]
  cat(sprintf("\n--- %s (%s -> %s) ---\n", cfg$dataset, cfg$start_period, cfg$end_period))

  data <- read.csv(cfg$dataset, stringsAsFactors = FALSE)
  data$time <- as.Date(data$time)

  res <- calculate_all_indices(data, cfg$start_period, cfg$end_period)
  cbind(dataset = cfg$dataset, start_period = cfg$start_period,
        end_period = cfg$end_period, res, stringsAsFactors = FALSE)
}))

# --------------------------------------------------------------------------
# Save results
# --------------------------------------------------------------------------
cat("\nSaving results to price_indices_results.csv\n")
write.csv(all_results, "price_indices_results.csv", row.names = FALSE)

# --------------------------------------------------------------------------
# Print results table
# --------------------------------------------------------------------------
cat("\n========================================\n")
cat("  BILATERAL PRICE INDEX RESULTS\n")
cat("========================================\n\n")

prev_dataset <- ""
prev_periods <- ""
for (i in seq_len(nrow(all_results))) {
  r <- all_results[i, ]
  if (r$dataset != prev_dataset || paste(r$start_period, r$end_period) != prev_periods) {
    if (prev_dataset != "") cat("\n")
    cat(sprintf("  [%s  %s -> %s  products: %s]\n\n",
                r$dataset, r$start_period, r$end_period, r$num_products))
    prev_dataset <- r$dataset
    prev_periods <- paste(r$start_period, r$end_period)
  }
  cat(sprintf("  %-25s %15s  %10ss  %s products\n",
              r$index_name, r$value, r$time_seconds, r$num_products))
}

cat("\n========================================\n")
cat(sprintf("Total indices calculated: %d\n", nrow(all_results)))
cat(sprintf("Datasets: %s\n", paste(unique(all_results$dataset), collapse = ", ")))
cat(sprintf("Output file: price_indices_results.csv\n"))
