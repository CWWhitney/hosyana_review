# ============================================================
# PRISMA flow figure from data/prisma/prisma_counts_full.csv
# plot_prisma(prisma)  ->  ggplot object
# All numbers come from the pipeline: nothing typed by hand.
# ============================================================

library(ggplot2)

plot_prisma <- function(prisma) {

  # helper: n of the row whose item starts with a text
  pn <- function(start) prisma$n[startsWith(prisma$item, start)][1]
  fm <- function(x) format(x, big.mark = ",")

  # sums by stage
  n_dup  <- sum(prisma$n[prisma$stage == "dedup"])
  n_scr  <- sum(prisma$n[prisma$stage == "screening"])
  n_lib  <- pn("Records in Zotero")
  n_inc  <- pn("TOTAL included")
  n_ver  <- pn("Verified")
  n_notv <- n_inc - n_ver

  # one row per box: centre x, centre y, width, height, text
  boxes <- data.frame(
    x = c(-4.2, 0, 4.2,   0,    5.6,   0,     5.6,    0,   -3.2,  3.2),
    y = c(  10, 10, 10,   7.6,  7.6,   5.2,   5.2,    2.8,    0,    0),
    w = c(  3.6, 3.6, 3.6, 4.4, 4.6,   4.4,   4.6,    4.4,  4.6,  5.4),
    h = c(  1.3, 1.3, 1.3, 1.3, 1.7,   1.3,   1.7,    1.3,  1.5,  1.9),
    label = c(
      paste0("Google Scholar\n", fm(pn("Google Scholar")), " (reported)"),
      paste0("Web of Science\n", fm(pn("Web of Science")), " (reported)"),
      paste0("CABI\n", fm(pn("CABI")), " (reported)"),
      paste0("Records in Zotero export\n", fm(n_lib)),
      paste0("Duplicates removed: ", fm(n_dup), "\ncitekey ", fm(pn("Removed: same citekey")),
             ", DOI ", pn("Removed: same DOI"), ",\ntitle+year ", pn("Removed: same title"),
             ", by hand ", pn("Removed: same work")),
      paste0("Records screened\n", fm(n_lib - n_dup)),
      paste0("Removed: ", fm(n_scr), "\nmanual 'bin' ", pn("Removed: manual"),
             ", automatic rules ", n_scr - pn("Removed: manual")),
      paste0("Included\n", fm(n_inc)),
      paste0("Verified in Crossref\n", fm(n_ver)),
      paste0("Not verified: ", fm(n_notv), "\nno DOI ", fm(pn("Not verified: no DOI")),
             ", not in Crossref ", pn("Not verified: DOI not in"), ",\nother work ",
             pn("Not verified: DOI points"), ", title missing ", pn("Not verified: our title"))
    ),
    fill = c(rep("grey90", 3), "white", "#fbe3e3", "white", "#fbe3e3", "#e3f1e3", "#e3f1e3", "#fdf0d5")
  )

  # arrows between boxes: from (x,y) to (xend,yend)
  arrows <- data.frame(
    x    = c(-4.2, 0, 4.2, 0,   0,   0,   0,   0,    0),
    y    = c(9.35, 9.35, 9.35, 6.95, 7.6, 4.55, 5.2, 2.15, 2.15),
    xend = c(0,    0,    0,    0,   3.3, 0,   3.3, -3.2,  3.2),
    yend = c(8.9,  8.9,  8.9,  5.85, 7.6, 3.45, 5.2, 0.75, 0.95)
  )
  # (first three arrows end at the library box: dashed, because identification counts are only reported)

  ggplot() +
    geom_segment(data = arrows, aes(x = x, y = y, xend = xend, yend = yend),
                 arrow = arrow(length = unit(0.18, "cm")), colour = "grey40") +
    geom_rect(data = boxes, aes(xmin = x - w / 2, xmax = x + w / 2, ymin = y - h / 2, ymax = y + h / 2, fill = fill),
              colour = "grey30") +
    geom_text(data = boxes, aes(x = x, y = y, label = label), size = 3.3, lineheight = 0.95) +
    scale_fill_identity() +
    coord_fixed(xlim = c(-7, 9), ylim = c(-1.2, 11)) +
    theme_void() +
    labs(caption = "Identification counts are as reported at search time (not checkable from files).\nEverything from the Zotero export onwards is counted by R/prisma_pipeline.R.")
}
