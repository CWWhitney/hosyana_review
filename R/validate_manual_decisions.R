validate_manual_decisions <- function(bib_data) {
  # Check that read papers without bin are always included
  read_papers <- bib_data %>%
    filter(has_read & !has_bin)
  
  incorrectly_excluded <- read_papers %>%
    filter(final_decision != "include")
  
  # Check that bin papers are always excluded  
  bin_papers <- bib_data %>%
    filter(has_bin)
  
  incorrectly_included <- bin_papers %>%
    filter(final_decision != "exclude")
  
  return(list(
    read_papers_total = nrow(read_papers),
    read_papers_correctly_included = nrow(read_papers) - nrow(incorrectly_excluded),
    read_papers_incorrectly_excluded = nrow(incorrectly_excluded),
    bin_papers_total = nrow(bin_papers),
    bin_papers_correctly_excluded = nrow(bin_papers) - nrow(incorrectly_included),
    bin_papers_incorrectly_included = nrow(incorrectly_included)
  ))
}