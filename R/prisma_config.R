# PRISMA exclusion criteria
prisma_criteria <- list(
  duplicates = c("duplicate", "copy", "reprint"),
  document_types = c("annual report", "syllabus", "catalog", "course notes", 
                     "legal document", "bibliography collection"),
  languages = c("non-english"),
  content_irrelevant = c("unrelated", "not relevant", "no decision focus")
)