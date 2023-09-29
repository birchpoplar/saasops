# Generating Exports

# Export to XLSX & PPTX

Objective of this function is to export data to formats suitable for compiling into a final presentation or report. Default exports of tables and charts to XLSX and PPTX is included:

	$ saasops export all 2023-03-01 2023-06-30
	
!!! note
    The function currently relies on a PPTX template file, which should be located at `exports/ppt_template.pptx`. The slide template ID is currently hardcoded in Python, and may need adjusting to suit your specific template. Search for the `add_chart_slide()` function in `src/export.py`. This functionality will be improved soon.
	
# Export image charts

Chart images can be generated as follows:

	$ saasops export charts 2023-03-01 2023-06-30
	
Output images will be stored in the `/exports` folder.

Gridlines can be included on various of the charts by passing the following flag:

	--show-gridlines
