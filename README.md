# Arch-Deflection-Analysis
In this project, we analyze the deflection behavior of 10 arches measured under laboratory conditions using two evaluation methods: AMO and ASTM. For each arch, deflection was recorded at 24 evenly spaced angles around 360°, and each angle was tested five times to ensure measurement reliability.

The raw experimental data were processed using Python. For each arch, method, and angle, I computed the mean deflection, standard deviation, and 95% confidence intervals. To capture the periodic deformation pattern, I applied a second-order harmonic regression model based on trigonometric functions. Because each arch has a different initial reference orientation, I also implemented a phase-alignment procedure based on dominant harmonic components to align peak deflections across specimens. This allowed meaningful comparison and aggregation of angular deflection patterns.

After alignment, I generated individual and grouped visualizations, including error-bar plots, harmonic fit curves, and multi-arch comparisons. I also identified common peak and valley locations from group-level harmonic fitting.

Overall, this workflow combines experimental data, statistical analysis, and signal modeling to study directional anisotropy and structural deformation patterns of arches under standardized testing conditions.
