#!/usr/bin/env Rscript

# Bilateral Price Index Calculator
# Uses the PriceIndices R package (https://cran.r-project.org/web/packages/PriceIndices/index.html)

# Install PriceIndices if not already installed
if (!requireNamespace("PriceIndices", quietly = TRUE)) {
  install.packages("PriceIndices", repos = "https://cloud.r-project.org")
}

library(PriceIndices)

# Load synthetic price data
data <- read.csv("price_data.csv", stringsAsFactors = FALSE)

# Ensure the time column is Date type
data$time <- as.Date(data$time)

# Define comparison periods
start_period <- "2024-01"
end_period   <- "2024-02"

cat("Calculating bilateral price indices between", start_period, "and", end_period, "\n\n")

# --------------------------------------------------------------------------
# 1) Unweighted bilateral indices
# --------------------------------------------------------------------------
unweighted_indices <- list(
  Jevons    = jevons(data, start = start_period, end = end_period),
  Carli     = carli(data, start = start_period, end = end_period),
  Dutot     = dutot(data, start = start_period, end = end_period),
  Harmonic  = harmonic(data, start = start_period, end = end_period),
  BMW       = bmw(data, start = start_period, end = end_period),
  CSWD      = cswd(data, start = start_period, end = end_period),
  Dikhanov  = dikhanov(data, start = start_period, end = end_period),
  YBMD      = ybmd(data, start = start_period, end = end_period)
)

# --------------------------------------------------------------------------
# 2) Weighted bilateral indices
# --------------------------------------------------------------------------
weighted_indices <- list(
  Fisher             = fisher(data, start = start_period, end = end_period),
  Laspeyres          = laspeyres(data, start = start_period, end = end_period),
  Paasche            = paasche(data, start = start_period, end = end_period),
  Tornqvist          = tornqvist(data, start = start_period, end = end_period),
  Walsh              = walsh(data, start = start_period, end = end_period),
  Sato_Vartia        = sato_vartia(data, start = start_period, end = end_period),
  Marshall_Edgeworth = marshall_edgeworth(data, start = start_period, end = end_period),
  Lloyd_Moulton      = lloyd_moulton(data, start = start_period, end = end_period, sigma = 0.9),
  Drobisch           = drobisch(data, start = start_period, end = end_period),
  Stuvel             = stuvel(data, start = start_period, end = end_period),
  Geo_Laspeyres      = geolaspeyres(data, start = start_period, end = end_period),
  Geo_Paasche        = geopaasche(data, start = start_period, end = end_period),
  Geo_Walsh          = geowalsh(data, start = start_period, end = end_period),
  Bialek             = bialek(data, start = start_period, end = end_period),
  Palgrave           = palgrave(data, start = start_period, end = end_period),
  AG_Mean            = agmean(data, start = start_period, end = end_period),
  Banajree           = banajree(data, start = start_period, end = end_period),
  Davies             = davies(data, start = start_period, end = end_period),
  Lehr               = lehr(data, start = start_period, end = end_period),
  Vartia             = vartia(data, start = start_period, end = end_period),
  Theil_I            = theil1(data, start = start_period, end = end_period),
  Theil_II           = theil2(data, start = start_period, end = end_period),
  Geo_Lowe           = geolowe(data, start = start_period, end = end_period),
  Geo_Young          = geoyoung(data, start = start_period, end = end_period),
  Geo_Hybrid         = geohybrid(data, start = start_period, end = end_period),
  Hybrid             = hybrid(data, start = start_period, end = end_period),
  HLC                = hlc(data, start = start_period, end = end_period),
  Walsh_Vartia       = walsh_vartia(data, start = start_period, end = end_period),
  Value_Index        = value_index(data, start = start_period, end = end_period),
  Unit_Value_Index   = unit_value_index(data, start = start_period, end = end_period)
)

# --------------------------------------------------------------------------
# Combine all results into a single data frame
# --------------------------------------------------------------------------
all_indices <- c(unweighted_indices, weighted_indices)

results <- data.frame(
  index_name = names(all_indices),
  value      = as.numeric(all_indices),
  stringsAsFactors = FALSE
)

# Format values to at least 7 decimal places in the CSV
results$value <- sprintf("%.7f", results$value)

# Save results
cat("Saving results to price_indices_results.csv\n\n")
write.csv(results, "price_indices_results.csv", row.names = FALSE)

# Print results table
cat("\n========================================\n")
cat("  BILATERAL PRICE INDEX RESULTS\n")
cat("========================================\n\n")
printf_row <- function(name, val) cat(sprintf("  %-25s %s\n", name, val))
for (i in seq_len(nrow(results))) {
  printf_row(results$index_name[i], results$value[i])
}
cat("\n========================================\n")
cat(sprintf("Total indices calculated: %d\n", nrow(results)))
cat(sprintf("Output file: price_indices_results.csv\n"))