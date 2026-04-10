# Price Indices Example

Example of bilateral price index calculations using the R [PriceIndices](https://cran.r-project.org/web/packages/PriceIndices/index.html) package with synthetic scanner data.

## Files

| File | Description |
|------|-------------|
| `price_data.csv` | Synthetic price data for 14 milk products across 2 outlets in January and February 2024 |
| `calculate_indices.R` | R script that computes 38 bilateral price indices (8 unweighted + 30 weighted) |
| `price_indices_results.csv` | Output CSV with index names and values (7 decimal places) |

## Data Format

The input CSV follows the [PriceIndices](https://cran.r-project.org/web/packages/PriceIndices/index.html) expected schema:

- `time` — transaction date (YYYY-MM-DD)
- `prices` — unit price (EUR)
- `quantities` — quantity sold (liters)
- `prodID` — unique product identifier
- `retID` — outlet/retailer identifier
- `description` — product label

## Calculated Indices

### Unweighted
Jevons, Carli, Dutot, Harmonic, BMW, CSWD, Dikhanov, YBMD

### Weighted
Fisher, Laspeyres, Paasche, Tornqvist, Walsh, Sato-Vartia, Marshall-Edgeworth, Lloyd-Moulton, Drobisch, Stuvel, Geo-Laspeyres, Geo-Paasche, Geo-Walsh, Bialek, Palgrave, AG Mean, Banajree, Davies, Lehr, Vartia, Theil I, Theil II, Geo-Lowe, Geo-Young, Geo-Hybrid, Hybrid, HLC, Walsh-Vartia, Value Index, Unit Value Index

## Usage

```bash
Rscript calculate_indices.R
```

## Reference

Białek, J. (2021). PriceIndices – a New R Package for Bilateral and Multilateral Price Index Calculations, *Statistika – Statistics and Economy Journal*, Vol. 2/2021, 122-141.

## License

MIT