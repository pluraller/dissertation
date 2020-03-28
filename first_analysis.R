---
title: 'analysis'
output: hmtl_document
---

```{r setup, include=FALSE}
library(ggplot2)
library(ggfortify)
library(lme4)
library(broom)
library(car)
library(readxl)
library(lmerTest)
library(psych)
library(tidyverse)
```

```{r}
timing <- fullreworked$Timing
stimlengths <- factor(fullreworked$`Stim length`)
fullreworked$`log(Timing)` <- log(fullreworked$Timing)
timing_log <- fullreworked$`log(Timing)`
totallangs <- fullreworked$`no. languages known`
lang_group <- factor(fullreworked$`Language Group`)
fullreworked$`Response ID` <- factor(fullreworked$`Response ID`)
responseID <- fullreworked$`Response ID`
```

## CHECK FOR INDEPENDENCE OF PARTICIPANTS

```{r}
leveneTest(timing, responseID)
leveneTest(timing, lang_group)
```

heteroscedastic measurements
(F=1.67, p=0.000000177)
(F=8.215, p=0.000275)


```{r}
kruskal.test(timing, responseID)
kruskal.test(timing, lang_group)
```
(Chi square=768.11, DF=164, p=2.2e-16)
kruskal wallis shows us significant differences between groups, can determine that participants are independent

```{r}
ggplot(data=fullreworked, aes(x= lang_group, y=timing, group=lang_group, color=lang_group)) + geom_boxplot(outlier.shape='cross') + ylab('Response time (s)') + xlab('Language group') + labs(color='')
```

plotting SD by participant
```{r}
ID_SD <- aggregate(formula = fullreworked$Timing ~ fullreworked$`Response ID` ,data = fullreworked, FUN = SD)
names(ID_SD)[names(ID_SD) == "fullreworked$`Response ID`"] <- "ID"
names(ID_SD)[names(ID_SD) == "fullreworked$Timing"] <- "Timing"
ggplot(data=ID_SD, aes(x = seq(1, length(ID)), y = Timing)) + geom_point() + xlab('Participant number') + ylab('Participant SD')
```


## stim length affect on timing
``` {r}
ggplot(data=fullreworked, aes(fullreworked$`Stim length`, fullreworked$Timing)) + geom_point() + geom_smooth(method='lm') + xlab('Stimulus length by number of words') + ylab('Response time by seconds') + geom_jitter()
```

# Fit a linear model, visualise assumptions
```{r}
stimlength_mod <- lm(timing ~ stimlengths, data = fullreworked)
par(mfrow = c(2, 2))
plot(stimlength_mod)
```
Residuals vs Fitted: data seems roughly linear (resid vs fitted)
Normal QQ plot: for normality of residuals definitely not normal, as shown by Q-Q plot
```{r}
shapiro.test(timing)
```

try removing outliers to see if this sorts it
#SIGNIFCANT AT ALPHA =0.01

```{r}
cooky_stimlength <- cooks.distance(stimlength_mod)
plot(cooky_stimlength, pch="*", cex=2, main="Influential Obs by Cook's distance\n from regression line response time ~ stimulus length", ylab= "Cook's distance")
sample_size <- nrow(fullreworked)
abline(h = 4/sample_size, col="red")
influential_stimlength <- as.numeric(names(cooky_stimlength)[(cooky_stimlength > (4/sample_size))])
reworked_trimmed_stimlength <- fullreworked[-influential_stimlength, ]
```

plot new corrected data

```{r}

ggplot(data= reworked_trimmed_stimlength, aes(x=reworked_trimmed_stimlength$`Stim length`, y=reworked_trimmed_stimlength$Timing)) + geom_point() +
  geom_smooth(method='lm') + xlab('Length of stimulus by number of words') +
  ylab('Response time (s)') + geom_jitter() + ggtitle('Length of stimulus against response time with linear regression line')
```

CAN SEE FROM DIFFERENT SLOPES THERE IS AN INTERACTION BETWEEN LANG GROUP AND STIMULI LENGTH

make new linear model

```{r}
stimlength_mod_cooked <- lm(timing ~ stimlengths, data = reworked_trimmed_stimlength)
par(mfrow = c(2, 2))
plot(stimlength_mod_cooked)
```

do a Spearman's rank correlation instead

```{r}
cor.test(reworked_trimmed_stimlength$`Stim length`, reworked_trimmed_stimlength$Timing, method=('spearman'))
```
there's a Rho value of 0.2978 and p(<2.2e-16). A slight correlation between stimulus length and response time. This was expected, but a correlation this weak is odd. suggests that stimulus length is a factor but not that influential
#SIGNIFICANT AT ALPHA =0.01

```{r}
trim_stim <- reworked_trimmed_stimlength$`Stim length`
trim_timing <- reworked_trimmed_stimlength$Timing
lang_groups_T <- reworked_trimmed_stimlength$`Language Group`


ggplot(data=reworked_trimmed_stimlength, aes(x = trim_stim, y = trim_timing)) + 
  geom_point() +
  geom_smooth(method='lm') + xlab('Stimulus length by number of words') + ylab('Response time (s)')

ggplot(data=reworked_trimmed_stimlength, aes(x = trim_stim, y=trim_timing, group=trim_stim)) + geom_boxplot() + xlab('Stimulus length by number of words') + ylab('Response time (s)')

ggplot(data=reworked_trimmed_stimlength, aes(x=trim_stim, fill=lang_groups_T)) + geom_histogram(na.rm=TRUE, bins=20) + xlab('Stimulus length by number of words') + ylab('Frequency') + guides(fill=guide_legend(title="Language group"))

```
## Total languages known against timing

Plot total languages against timing

```{r}
ggplot(data = fullreworked, aes(x = totallangs, y = timing_log)) +
  geom_point() +
  ylim(c(0, 250)) +
  geom_smooth(method = 'lm') + ylim(0,6) + geom_jitter(width=0.1, height=0) + 
  xlab('Total languages known') +
  ylab('log(Response time (s)')

ggplot(data=fullreworked, aes(x = totallangs, y=timing_log, group=totallangs)) + geom_boxplot() + xlab('Number  of languages known') + ylab('log(Response time (s))')

ggplot(data=fullreworked, aes(x=totallangs, fill=lang_group)) + geom_histogram(na.rm=TRUE, bins=20) + xlab('Total languages known') + ylab('Frequency') +  guides(fill=guide_legend(title="Language group"))
```

make a linear model

```{r}

totallang_mod <- lmer(timing_log ~ totallangs*stimlengths + (1|responseID), data=fullreworked)
summary(totallang_mod)
```

```{r}
cooky_total <- cooks.distance(totallang_mod)
plot(cooky_total, pch="*", cex=2, main="Influential Obs by Cooks distance")
abline(h = 4/sample_size, col="red")
influential_total <- as.numeric(names(cooky_total)[(cooky_total > (4/sample_size))])
reworked_trimmed_totals <- fullreworked[-influential_total, ]
```
```{r}
ks.test(residuals(totallang_mod), "pnorm", mean=mean(residuals(totallang_mod)), sd=sd(residuals(totallang_mod)))
shapiro.test(residuals(totallang_mod))
```
```{r}
leveneTest(residuals(totallang_mod), lang_group)
```


```{r}
ggplot(data= reworked_trimmed_totals, aes(x=reworked_trimmed_totals$`no. languages known`, y=reworked_trimmed_totals$Timing, color=reworked_trimmed_totals$`Language Group`)) + geom_point() + xlab('Number of languages known') + ylab('Response time (s)') +
  geom_smooth(method='lm') + labs(color='Language group')
```



##multilevel linear model

isolate my variables first

```{r}
stim_length_T <- reworked_trimmed_stimlength$`Stim length`
timing_T <- reworked_trimmed_stimlength$Timing
lang_groups_T <- reworked_trimmed_stimlength$`Language Group`
response_ID_T <- reworked_trimmed_stimlength$`Response ID`
totallangs_T <- reworked_trimmed_stimlength$`no. languages known`
```

plot trimmed data from stimlength/timing model

```{r}
ggplot(data = reworked_trimmed_stimlength, aes(x=stim_length_T, y=timing_T, color=lang_groups_T)) +
  geom_point() +
  geom_smooth(method=lm) + 
  xlab('Length of stimulus') + 
  ylab('Response time (s)') +
  labs(color='Language group')
```

run initial multilevel model

```{r}
multiple <- lmer(timing_T ~ lang_groups_T + stim_length_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(multiple)
```

check assumptions
1) homogeneity of variance across residuals by groups

```{r}
aug_mul <- augment(multiple)
leveneTest(aug_mul$.resid, aug_mul$lang_group)
```

no homogeneity of variance
#SIGNIFICANT AT ALPHA = 0.01 

2) normality of residuals

```{r}
shapiro.test(aug_mul$.resid)
```

#SIGNIFICANT AT ALPHA = 0.01
no normally distributed residuals, so will transmform outcomes

y <- log10(y)

try with ref as english

```{r}

timing_log_trim <- reworked_trimmed_stimlength$`log(Timing)`
ref <- relevel(factor(reworked_trimmed_stimlength$`Language Group`), ref = 'English')
multiple_log_E <- lmer(timing_log_trim ~ stim_length_T * ref + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(multiple_log_E)
```

SO
english and dutch have significant difference, Dutch slower at solving than English
also a sigificant interaction between eng and dutch
no signficant difference between between english and german ?
interactions:
stim length:Dutch interaction is significant, they respond differently to increase in stim length
stim length:German interaction is not significant, cant say that they respond dif to stim length, respond about the same as English
no interaction at all between total languages and response time even when taken in respect to stim length and language group
omit it from next analysis as a fixed effect



```{r}
ref <- relevel(factor(reworked_trimmed_stimlength$`Language Group`), ref = 'Dutch')
multiple_log_D <- lmer(timing_log_trim ~ stim_length_T * ref + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(multiple_log_D)
```

significant difference between german and dutch, and dutch and english
english quicker than dutch
german quicker than dutch
dutch slower than english
CANT SAY german slower than english
stim length interaction significant for stim length:English
stim length interaction signifiant for stim length:German
English responds differently to changes in stimulus length than Dutch
German responds differently to changes in stimulus length than Dutch
But English DOESNT respond differntly to changes in stimulus length than German

```{r}
last <- lmer(timing_log_trim ~ stim_length_T * lang_groups_T + (1|response_ID_T)-1, data=reworked_trimmed_stimlength)
summary(last)
```

new model with transmformed output
check assumptions again
```{r}
ref <- relevel(factor(reworked_trimmed_stimlength$`Language Group`), ref = 'German')
multiple_log_G <- lmer(timing_log_trim ~ stim_length_T * ref + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(multiple_log_G)
```

```{r}
aug_mul_log_E <- augment(multiple_log_E)
leveneTest(aug_mul_log_E$.resid, aug_mul_log_E$ref)
aug_mul_log_D <- augment(multiple_log_D)
leveneTest(aug_mul_log_D$.resid, aug_mul_log_D$ref)
```

found some homogeneity of variance at alpha =0.01
#INSIGNIFICANT AT ALPHA = 0.01
check normality of residuals

```{r}
ks.test(aug_mul_log_E$.resid, "pnorm", mean=mean(aug_mul_log_E$.resid), sd=sd(aug_mul_log_E$.resid))
ks.test(aug_mul_log_D$.resid, "pnorm", mean=mean(aug_mul_log_D$.resid), sd=sd(aug_mul_log_D$.resid))
```
#INSIGNIFICANT AT ALPHA = 0.01
found normal resid at alpha =0.01
#NICE

graph our results

```{r}
ggplot(data = reworked_trimmed_stimlength, aes(x=stim_length_T, y=timing_log_trim, color=lang_groups_T)) +
  geom_point() +
  geom_smooth(method=lm) +
  xlab('Stimulus length') +
  ylab('log(Timing) (seconds)') + labs(color='Language group')
```

checking effect size?
Xu, R. 2003. Measuring explained variation in linear mixed effects models. Statist. Med. 22:3527-3541. doi:10.1002/sim.1572

```{r}
1-var(residuals(multiple_log_E))/(var(model.response(model.frame(multiple_log_E))))
1-var(residuals(multiple_log_D))/(var(model.response(model.frame(multiple_log_D))))
```

##checking whether exposure + read exposure interaction is significant
# check for interactions

if significant, will check for further languages

```{r}
exposure_1_T <- reworked_trimmed_stimlength$`exposure %: Language 1` / 10 
read_exposure_1_T <- reworked_trimmed_stimlength$`read exposure % Language 1` / 10
exp_mod <- lmer(timing_log_trim ~ stim_length_T + exposure_1_T * read_exposure_1_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(exp_mod)

```

no significant effects of exposure and read exposure on language one
can safely assume that language 2+ will have same effects

```{r}
shapiro.test(residuals(exp_mod))
leveneTest(residuals(exp_mod), response_ID_T)
```
#INSIGNIFICANT AT ALPHA=0.01
meets both assumptions


##check whether depth of secondary languages have had effect on timing

#first check significant differences between samples 

```{r}
l2 <- fullreworked$`languages known: Language 2 - Text`
l3 <- fullreworked$`languages known: Language 3 - Text`
l4 <- fullreworked$`languages known: Language 4 - Text`
l5 <- fullreworked$`languages known: Language 5 - Text`
```
not normal, so do kruskal wallis

```{r}
kruskal.test(l2, l3, l4, l5)
```

population medians are not equal
__what does this mean?__


```{r}
lang2_mod <- lmer(timing_log_trim ~ stim_length_T + lang2_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(lang2_mod)
```
completely unsignificant again
 
 
try the other languages just for the crack 
```{r}
lang3_mod <- lmer(timing_log_trim ~ stim_length_T + lang3_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(lang3_mod)
```

insignificant again lol

```{r}
lang4_mod <- lmer(timing_log_trim ~ stim_length_T + lang4_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(lang4_mod)
```

still nada

```{r}
lang5_mod <- lmer(timing_log_trim ~ stim_length_T + lang5_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(lang5_mod)
```

```{r}
langs_mod <- lmer(fullreworked$`log(Timing)` ~ l2*l3*l4*l5 + fullreworked$`Stim length` + (1|responseID), data=fullreworked)
summary(langs_mod)
```
```{r}
shapiro.test(residuals(langs_mod))
aug_langs <- augment(langs_mod)
leveneTest(aug_langs$.resid, aug_langs$l2)
leveneTest(aug_langs$.resid, aug_langs$l3)
leveneTest(aug_langs$.resid, aug_langs$l4)
leveneTest(aug_langs$.resid, aug_langs$l5)
leveneTest(aug_langs$.resid, aug_langs$responseID)

```

```{r}
ggplot(plus, aes(LData, fill=LRank)) + geom_histogram()
```

```{r}
plus_mod <- lmer(plus$Timing ~ plus$Stim + plus$LData)
```


## CHECK FOR ORDER OF ACQUISITION
# check if order of acquisition had any effect on timing
#order1

```{r}
order1 <- factor(reworked_trimmed_stimlength$`order of acq: Language 1`)
order1mod <- lmer(timing_log_trim ~ stim_length_T + order1 + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(order1mod)
```

nope

#check order of acq of lang 2 w interaction for depth of lang 2

```{r}
order2 <- factor(reworked_trimmed_stimlength$`order of acq: Language 2`)
order2mod <- lmer(timing_log_trim ~ stim_length_T + order2*lang2_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(order2mod)
```

still insignificant

```{r}
order3 <- factor(reworked_trimmed_stimlength$`order of acq: Language 3`)
order3mod <- lmer(timing_log_trim ~ stim_length_T + order3*lang3_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(order3mod)
```

still nada

```{r}
order4 <- factor(reworked_trimmed_stimlength$`order of acq: Language 4`)
order5 <- factor(reworked_trimmed_stimlength$`languages known: Language 5 - Text`)
allorders <- lmer(timing_log_trim ~ order1*order2*order3*order4*order5 + stim_length_T + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(allorders)
```

##check if formal education has an effect on timing
```{r}
edu_level <- factor(reworked_trimmed_stimlength$`Please check your highest education level`)
edu_years <- reworked_trimmed_stimlength$`How many years of formal education do you have?`
edu_model <- lmer(timing_log_trim ~ stim_length_T + edu_level*edu_years + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(edu_model)
```

check assumptions
```{r}
shapiro.test(residuals(edu_model))
```
nicely normal
#INSIGNIFICANT AT ALPHA=0.01

__DONT KNOW WHY I HAVE FEWER RESIDUALS THAN VALUES?__
```{r}
leveneTest(residuals(edu_model), response_ID_T)
```

only thing close to significance is Some Graduate School and High School


## self diagnosed exposure categories against timing

```{r}
friends <- reworked_trimmed_stimlength$`Interacting with friends`
family <- reworked_trimmed_stimlength$`Interacting with family`
telly <- reworked_trimmed_stimlength$`Watching TV`
radio <- reworked_trimmed_stimlength$`Listening to radio/music`
reading <- reworked_trimmed_stimlength$Reading
categories_mod <- lmer(timing_log_trim ~ stim_length_T + friends * family * telly * radio * reading + (1|response_ID_T), data=reworked_trimmed_stimlength)
summary(categories_mod)


```

essentially no demographic data has a real effect
this is kinda good
know that in reality the only thing that has statistically effected my outcome is the language group

