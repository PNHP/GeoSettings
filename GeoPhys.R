library(tidyr)
library(classInt)
library(ggplot2)

elev <- read.csv("elevations.csv", stringsAsFactors = FALSE)
elev <- elev[c("Assoc_Alli","RASTERVALU")]
elev <- elev[elev$Assoc_Alli!=" ",]
elev1 <- separate_rows(elev, "Assoc_Alli")

elev1 <- elev1[complete.cases(elev1), ]

elev1 <- elev1[order(elev1$RASTERVALU), ]

ggplot(elev1, aes(reorder(Assoc_Alli, RASTERVALU, FUN=mean), RASTERVALU,color=Assoc_Alli)  ) + geom_point() + theme(legend.position="none") + theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  stat_summary(aes(y = RASTERVALU,group=1), fun.y=mean, colour="red", geom="line",group=1) 

aggdata <-aggregate(elev1, by=list(elev1$Assoc_Alli), FUN=mean, na.rm=TRUE)
aggdata$Assoc_Alli <- NULL
plot(aggdata$Group.1~aggdata$RASTERVALU)

classIntervals(aggdata$RASTERVALU,6,style="jenks")

