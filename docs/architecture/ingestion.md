# Ingestion Architecture

Ingestion accepts supported PDF/image inputs and creates a stable document identity plus page-aware representation.

Preserve page numbers and source coordinates through every downstream stage so evidence can be mapped back to the original drawing.

For the prototype, local temporary storage is sufficient. Real confidential documents must not enter version control.
