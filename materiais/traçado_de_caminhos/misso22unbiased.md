Unbiased and consistent rendering using biased estimators
ZACKARY MISSO, Dartmouth College, USA
BENEDIKT BITTERLI, Dartmouth College, USA and NVIDIA, USA
ILIYAN GEORGIEV, Autodesk, United Kingdom
WOJCIECH JAROSZ, Dartmouth College, USA
We introduce a general framework for transforming biased estimators into
unbiased and consistent estimators for the same quantity. We show how
several existing unbiased and consistent estimation strategies in rendering
are special cases of this framework, and are part of a broader debiasing prin-
ciple. We provide a recipe for constructing estimators using our generalized
framework and demonstrate its applicability by developing novel unbiased
forms of transmittance estimation, photon mapping, and finite differences.

```
CCS Concepts: • Computing methodologies → Rendering; Ray trac-
```

ing.
Additional Key Words and Phrases: Monte Carlo, infinite series, Taylor series
ACM Reference Format:
Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz. 2022.
Unbiased and consistent rendering using biased estimators. ACM Trans.

```
Graph. 41, 4, Article 48 (July 2022), 13 pages. https://doi.org/10.1145/3528223.
```

3530160
1 INTRODUCTION
From estimating the amount of radiance reaching a camera sensor,
to estimating how much light transmits through a participating
medium, there are countless situations in graphics which require
estimating intricate integrals. While we have developed a large ar-
senal of unbiased estimation techniques, situations still arise where
we must fall back on biased formulations.
We consider problems where we need to compute some finite

```
quantity 𝐼 , but we only have a biased estimator ⟨𝐼 (𝑘)⟩ with a control-
```

lable amount of bias—dictated by some parameter 𝑘—at our disposal.

```
By adjusting the bias parameter towards some limit (e.g. 𝑘 → ∞)
```

```
the estimator’s expected value 𝐼 (𝑘) approaches the correct answer:
```

```
𝐼 = lim𝑘→∞ 𝐼 (𝑘). (1)
```

```
The bias parameter 𝑘 could be continuous or discrete; for example,
```

a discrete 𝑘 could represent the maximum path length in a path
tracer, while a continuous 𝑘 could correspond to the step size in ray

```
marching or the kernel radius in photon mapping. We assume 𝐼 (∞)
```

cannot be estimated directly e.g. due to computational constraints,
and only biased estimates of 𝐼 for finite values of 𝑘 are available.

```
Authors’ addresses: Zackary Misso, zackary.t.misso.gr@dartmouth.edu, DartmouthCollege, USA; Benedikt Bitterli, benedikt.bitterli@gmail.com, Dartmouth College, USA
```

```
and NVIDIA, USA; Iliyan Georgiev, iliyan.georgiev@autodesk.com, Autodesk, UnitedKingdom; Wojciech Jarosz, wojciech.k.jarosz@dartmouth.edu, Dartmouth College,
```

USA.

```
© 2022 Copyright held by the owner/author(s). Publication rights licensed to ACM.This is the author’s version of the work. It is posted here for your personal use. Not for
```

redistribution. The definitive Version of Record was published in ACM Transactions onGraphics, https://doi.org/10.1145/3528223.3530160.

```
When faced with a situation like Eq. (1), one existing approach
```

in graphics is to at least form a consistent estimator in which both
bias and variance are guaranteed to vanish, though only in the limit
of infinite work. This can be done for certain classes of problems,

```
like progressive photon mapping approaches [Hachisuka et al . 2010;
```

```
Hachisuka and Jensen 2009; Jarosz et al . 2011b; Knaus and Zwicker
```

2011], by averaging realizations of the biased estimate while care-
fully controlling the bias parameter 𝑘 to ensure convergence.
In this paper we instead introduce and extend a recent set of
techniques from the statistics literature for entirely debiasing biased
estimators. Our framework can provide unbiased solutions to prob-
lems ranging from estimating transmittance in non-exponential
media, to computing unbiased derivatives, to creating unbiased

```
versions of entire global illumination algorithms like (progressive)
```

photon mapping.
To debias a chosen problem, we decompose the unbiased quantity

```
𝐼 = 𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘
Δ𝑗

```
𝐵 (𝑘)
```

```
(2)
```

```
into a biased value 𝐼 (𝑘) and an infinite sum representing the bias
```

```
𝐵(𝑘) B 𝐼 − 𝐼 (𝑘). We then form unbiased estimators for both terms.
```

There are many different ways to transform a problem into an in-

```
finite series in the form of Eq. (2), all differing by their construction
```

of Δ𝑗 . In the following two sections we will discuss two such trans-
formations and their utilization in prior work for isolated problems
in graphics. The first one involves eliminating the bias via a Taylor

```
series (Sec. 2), and the second does so via an initial-value integral or
```

```
a corresponding discrete telescoping-series transformation (Sec. 3).
```

```
In Sec. 4 we will discuss how to formulate estimators for Eq. (2)
```

which encompasses both the Taylor and telescoping formulations.

```
By carefully constructing estimators so that 𝐵(𝑘) vanishes in the
```

limit, we can formulate unbiased solutions for all problems in the

```
form of Eq. (2). However, not all such solutions can be achieved
```

with both finite variance and finite work, despite their guaranteed
eventual convergence by the law of large numbers. For those cases,

```
we show how to still formulate unbiased estimators (Sec. 4.4) and,
```

```
alternatively, derive consistent progressive estimators (Sec. 4.4).
```

We provide a general recipe for creating unbiased estimates out

```
of biased estimators (Recipe 1). In Sec. 5 we show how our recipe
```

can be applied to estimate a variety of problems, including novel
unbiased non-exponential transmittance [Bitterli et al . 2018] esti-

```
mation, unbiased variants of (progressive) photon-mapping, and
```

```
unbiased (for smooth functions) and progressive (for discontinuous
```

```
functions) finite difference estimators that can be used as ground
```

truth when developing differentiable rendering techniques. We pro-
vide full implementations on GitHub [Misso et al. 2022].
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:2 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz
2 TAYLOR-SERIES DEBIASING
One common problem that arises in graphics is the need to form
estimators for integrals 𝐹 which are nested inside some non-linear

```
function 𝑔:
```

```
𝐼 B 𝑔(𝐹 ) = 𝑔
```

```
(∫
```

```
Ω 𝑓 (𝑥) d𝑥
```

```
)
```

```
. (3)
```

For instance, 𝑔 could be the reciprocal function when estimating a
normalization factor, or the exponential function when estimating
volumetric transmittance. Naively applying Monte Carlo estimation
to the integral 𝐹 will generally yield a biased estimate if the function
𝑔 is non-affine. Outside of graphics, these types of problems are
referred to as functions of expectations [Blanchet et al. 2015].

```
Assuming 𝑔(𝐹 ) is finite and has a convergent Taylor series about
```

```
some expansion point 𝛼, we can express Eq. (3) as:
```

```
𝐼 B 𝑔(𝐹 ) =
```

𝑘−1Õ
𝑗=0
Δtay𝑗

```
𝐼 (𝑘)
```

- ∞Õ
  𝑗=𝑘
  Δtay𝑗

```
𝐵 (𝑘)
```

```
, with Δtay𝑗 = 𝑔( 𝑗) (𝛼) (𝐹 − 𝛼)
```

𝑗

```
𝑗! , (4)
```

```
where 𝑔( 𝑗) (𝛼) denotes the 𝑗th derivative of 𝑔 evaluated at 𝛼. For any
```

fixed bias parameter 𝑘, this decomposes 𝐼 into a biased formulation

```
𝐼 (𝑘) consisting of the first 𝑘 terms of the Taylor series, and the
```

```
remaining terms of the Taylor series constituting the bias 𝐵(𝑘). For
```

```
instance, when 𝑘 = 1, 𝐼 (𝑘) becomes just the evaluation of 𝑔 at the
```

```
expansion point, 𝑔(𝛼), which will generally be a biased evaluation
```

of 𝐼 unless we happen to choose an expansion point, 𝛼 = 𝐹 , equal
to the integral we want to estimate. The infinite sum then corrects

```
for this bias (see Fig. 1).
```

The Taylor expansion effectively separates the evaluation of 𝑔
from the eventual estimation of 𝐹 , thus removing the problematic

```
non-linearities. While (𝐹 −𝛼) 𝑗 is still a non-linear operation, we can
```

estimate it in an unbiased manner by treating it as the product of 𝑗

```
independent evaluations of (𝐹 − 𝛼) [Blanchet et al . 2015; Georgiev
```

et al. 2019].
0.0 0.2 0.4 0.6 0.8 1.0 1.20.0
0.5
1.0
1.5
2.0
2.5
3.0
3.5
4.0
4.5

```
𝑔(𝛼)
```

```
𝑔(𝐹 )
```

𝛼𝐹
𝐹 − 𝛼
V[⟨𝐹 ⟩ − 𝛼]
𝐵
...
Δ4
Δ3
Δ2
Δ1

```
𝑔(𝑥) = 1/𝑥
```

```
𝑔(𝛼)
```

```
+𝑔(1) (𝛼)(𝑥 − 𝛼)
```

```
+𝑔(2) (𝛼)(𝑥 − 𝛼)2/2!
```

```
+𝑔(3) (𝛼)(𝑥 − 𝛼)3/3!
```

```
+𝑔(4) (𝛼)(𝑥 − 𝛼)4/4!
```

```
+𝑔(5) (𝛼)(𝑥 − 𝛼)5/5!
```

Δ5

```
Fig. 1. Equation (4) enables the unbiased estimation of 𝑔(𝐹 ) using only
```

unbiased estimates ⟨𝐹 ⟩ of 𝐹 and the analytic derivatives of 𝑔. Starting with

```
𝐼 (1) = 𝑔(𝛼), it progressively adds terms (vertical colored bars labeled Δ𝑗 on
```

```
the left) of a Taylor series expansion of 𝑔(𝑥) (dashed curves), each evaluated
```

at a stochastic distance ⟨𝐹 ⟩ − 𝛼.
2.1 Prior work
The Taylor series has not yet been introduced to graphics as a

```
general debiasing technique; however, formulations like Eq. (4) have
```

appeared for problems like transmittance and reciprocal estimation,
though they initially arose via other mathematical manipulations.
We will show how these specific instances can be easily derived

```
directly from Eq. (4).
```

Reciprocal estimation. We sometimes need to estimate the recip-
rocal of an integral,

```
𝑔(𝐹 ) B 1𝐹 . (5)
```

For instance, this happens in both photon mapping [Qin et al . 2015]
and differentiable rendering [Bangaru et al . 2020] where 𝐹 is a Monte

```
Carlo sampling probability (density) that is not available in closed
```

form, so its reciprocal must be estimated numerically. Applying

```
Eq. (4) to Eq. (5), choosing 𝑘 = 1, and performing some elementary
```

simplifications provides

```
𝑔(𝐹 ) = 1𝛼 +
```

∞Õ
𝑗=1

```
Δrecip𝑗 , where Δrecip𝑗 = 𝛼−𝑗−1 (𝛼 − 𝐹 ) 𝑗 , (6)
```

which can be readily estimated in an unbiased way provided 𝛼 ≠ 0.
Unbiased reciprocal estimation was first introduced to graphics
by Qin et al . [2015] where they imported the technique directly from
the nuclear engineering literature [Booth 2007]. Booth originally

```
derived his formulation by applying control variates to Eq. (5), then
```

```
effectively taking a Maclaurin series expansion (Taylor series about
```

```
𝛼 = 0) by pattern matching with the well-known analytical solution
```

of the geometric series.
Applying control variates then taking a Maclaurin series expan-
sion is equivalent to taking the Taylor series expansion where 𝛼 is

```
set to the control. Thus, our formulation (6) generalizes the control
```

```
function Booth introduced in his derivation. The Bernoulli trial esti-
```

mation technique later introduced by Qin et al . [2015]—which has
also been used for specular manifold sampling [Zeltner et al . 2020]
and path connections in refractive media [Pediredla et al . 2020]—is

```
a special case of a prefix sum estimator (Sec. 4) for Eq. (6) when
```

```
estimating a reciprocal probability (density). We show that it is also
```

a special case of the pseries-cumulative estimator [Georgiev et al .
2019] adapted for reciprocal estimation within our full implementa-
tion [Misso et al. 2022].
Exponential-transmittance estimation. Estimating the proportion
of light which passes through a participating medium is a core
component in simulating volumetric transport. The classical trans-
mittance is defined as

```
𝑔(𝐹 ) B e−𝐹 , (7)
```

```
where 𝐹 = 𝜏 B ∫ 𝑏𝑎 𝜇 (𝑥) d𝑥 is the optical depth integral over the
```

medium extinction.

```
Applying Eq. (4) to (7) , setting 𝑘 = 1 and performing some ele-
```

mentary simplifications allows us to express transmittance as

```
𝑔(𝐹 ) = e−𝛼 +
```

∞Õ
𝑗=1

```
Δexp𝑗 , where Δexp𝑗 = e−𝛼 (𝛼 − 𝐹 )
```

𝑗

```
𝑗! , (8)
```

which is amenable to unbiased estimation.
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:3
Both Georgiev et al . [2019] and Jonsson et al . [2020] introduced

```
formulations for exponential transmittance equivalent to Eq. (8),
```

however, both of these were obtained in a similar fashion to Booth’s
[2007] derivations for the reciprocal: they first applied control vari-

```
ates directly to Eq. (7) to introduce a majorant, and then applied
```

```
a power (Maclaurin) series expansion to the resulting exponential.
```

One of the major insights from Georgiev et al. ’s derivations was
that the majorant used by all prior null-collision based tracking
estimators corresponds to a simple application of control variates.
In contrast, we have arrived at the same formulation as a di-
rect consequence of applying the Taylor series at a user-chosen
expansion point 𝛼. Our derivation shows that the majorant in null-
scattering methods is simply the Taylor series expansion point.
Kettunen et al . [2021] developed a prefix-sum based estimator for
classical transmittance which exploits the expansion point used in
the Taylor expansion of the exponential function along with a few
other techniques for variance reduction. Their final estimator had a

```
form similar to Eq. (4). They pointed out that if the first term in their
```

```
formulation was separated from the infinite sum (i.e. 𝑘 = 1), then
```

their estimator debiases an instance of ray-marching. Our derivation
shows that all prior unbiased transmittance estimators which are
derived from a Taylor series expansion can be thought of as a form
of debiased estimation. We will discuss why this is also true for the
Volterra based estimators [Georgiev et al. 2019] in Sec. 3.3.
Outside of graphics. Blanchet et al . [2015] introduced the idea
of the Taylor series as a generalized means of formulating unbi-
ased estimators for functions of expectations. Dauchet et al. [2018]
mentions this idea too in the context of handling non-linearities
with Monte Carlo. Outside of these instances, the Taylor expansion
has been utilized throughout statistics to reduce bias of general

```
estimators of differentiable functions [Jiao and Han 2020; Withers
```

1987].
3 INITIAL-VALUE & TELESCOPING-SERIES DEBIASING
While the Taylor expansion is effective in situations where we deal
with smooth functions of expectations, unfortunately not all prob-
lems can be represented this way. Either the function does not have
a convergent Taylor series, or a problem may simply not fit within

```
the narrow scope of a function of expectations (3) , even if it is an
```

```
instance of Eq. (1). To handle this, we first derive a continuous for-
```

mulation, and then show how once it is discretized, it simplifies
to a debiasing technique developed recently within the statistics
literature.
3.1 Continuous formulation
For any 𝑘, we can define the relationship between the limit 𝐼 and

```
the expectation 𝐼 (𝑘) of a biased estimate by manipulating Eq. (2),
```

```
𝐼 = 𝐼 (𝑘) + 𝐵(𝑘) = 𝐼 (𝑘) + 𝐼 (∞) − 𝐼 (𝑘). (9)
```

Assuming that 𝑘 is a continuous parameter and that the derivative

```
of 𝐼 w.r.t. 𝑘 exists, we can rewrite Eq. (9) as an initial value problem:
```

```
𝐼 = 𝐼 (𝑘) +
```

∫ ∞
𝑘
d

```
d𝑥 𝐼 (𝑥) d𝑥 . (10)
```

```
This formulation is a continuous version of Eq. (2) for debiasing a
```

biased quantity, by integrating how the bias changes as we change
the variable 𝑘 dictating the bias.
3.2 Discrete formulation

```
Many of the problems defined by Eq. (1) involve 𝑘’s which are
```

discrete instead of continuous. We can obtain a discrete analog to

```
Eq. (10) by splitting the integral into a sum of unit-length integrals,
```

```
𝐼 = 𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘
∫ 𝑗+1
𝑗
d

```
d𝑥 𝐼 (𝑥) d𝑥 . (11)
```

By replacing the integral over the derivative with its anti-derivative,
we arrive at

```
𝐼 = 𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘

```
Δtele𝑗 , where Δtele𝑗 = 𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗). (12)
```

This is an infinite telescoping sum of readily estimatable expecta-

```
tions, similar to Eq. (4). Note, that any finite sum up to 𝑘 of Δtele𝑗 ,
```

```
simplifies to 𝐼 (𝑘).
```

3.3 Prior work
Path tracing. Path tracing computes an unbiased estimate of an
image by accumulating the contribution from all length paths. If we

```
define 𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗) to represent the difference between ( 𝑗 + 1)-
```

length transport and 𝑗-length transport, i.e. the contribution of only

```
the ( 𝑗 + 1)-st bounce (see Fig. 2), we can interpret path tracing as
```

```
an instance of a telescoping sum (12) which compensates for the
```

bias of direct illumination by evaluating each additional path length
up to infinity. We further show that Russian roulette termination

```
in path tracing becomes a single-term estimation strategy (Sec. 4)
```

```
applied to Eq. (12) in the case of naive path-tracing with no next-
```

event estimation and no scattering on emissive surfaces. Otherwise,
it becomes an instance of a prefix-sum based estimation strategy.
Volterra transmittance. Georgiev et al . [2019] introduced an inte-
gral formulation for estimating transmittance in a classical medium
which they derived by starting from a reduced form of the differen-
tial radiative transfer equation.

```
If we define 𝐼 B lim𝑘→𝑏 𝐼 (𝑘) where 𝑏 is the distance to the end
```

of a path segment, and we plug in the definition of exponential

```
Í20𝑗=0[𝐼 ( 𝑗 +1) − 𝐼 ( 𝑗)] 𝐼 (1) − 𝐼 (0) 𝐼 (2) − 𝐼 (1) 𝐼 (3) − 𝐼 (2)
```

```
Fig. 2. Illustration of path tracing as an instance of Eq. (12). Each term in the
```

```
summation is the difference in contribution between ( 𝑗 +1)- and 𝑗-length
```

paths, simplifying to a sum over the contribution of various bounces.
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:4 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz

```
transmittance 𝐼 = Tr(𝑘, 𝑏) B e−
```

∫ 𝑏

```
𝑘 𝜇 (𝑦) d𝑦 into Eq. (10), we obtain
```

```
Tr(𝑘, 𝑏) = Tr(𝑘, 𝑘) +
```

∫ 𝑏
𝑘
d

```
d𝑥 Tr(𝑥, 𝑏) d𝑥
```

= 1 −
∫ 𝑏

```
𝑘𝜇 (𝑥) Tr(𝑥, 𝑏) d𝑥 .
```

```
(13)
```

This is the same as Georgiev et al . ’s [2019] Volterra formulation,
except instead of starting from the radiative transfer equation, which
is not easily generalized to non-exponential transmittance functions,

```
we derived via Eq. (10). This representation was used by Vicini et al .
```

[2021] to formulate a non-exponential transmittance model which
allows for learning improved volumetric scene representations.
Outside of classical transmittance estimation, we found the appli-

```
cation of Eq. (10) to perform worse than Eq. (12) due to the deriva-
```

tives in the continuous case having unbounded variance. For this
reason, we will choose to focus on the discrete formulation instead,
however, everything we will cover generalizes nicely to the contin-
uous case as well.
Reciprocal estimation. Bangaru et al . [2020] introduced an unbi-
ased differentiable rendering algorithm which utilized the diver-
gence theorem to handle discontinuous integrands. Their formu-
lations introduced a discontinuous warp field which they make
continuous through convolution with a smoothing kernel whose
normalization factor is scene-dependent and must be estimated.
This amounts to formulating unbiased estimates for the reciprocal

```
of a random variable for which either Eq. (4) or Eq. (12) could be used.
```

Bangaru et al . [2020] utilized the estimator proposed by McLeish

```
[2011] which is an instance of Eq. (12).
```

Outside of graphics. Within the statistical literature, McLeish
[2011] and Rhee and Glynn [2012] independently introduced the

```
first estimation schemes for Eq. (12). Rhee and Glynn focused on
```

the specific problem of creating unbiased estimators for stochastic

```
differential equations (SDEs) by adding randomized truncation (akin
```

```
to Russian roulette) to multi-level Monte Carlo [Giles 2008; Hein-
```

```
rich 1998; Keller 2001]. McLeish [2011] introduced a more general
```

estimator using a prefix-sum that we’ll discuss in Sec. 4.
Rhee [2013] analyzed the optimal design decisions in creating esti-

```
mators for Eq. (12) and later Blanchet et al. [2015] equated this with
```

the optimal design decisions for the Taylor expansion approach in

```
Eq. (4). Rhee and Glynn [2015] later used these findings to introduce
```

practical estimators for SDEs while Blanchet et al . [2015] introduced
a variance reduction technique to improve the convergence rate of
a certain class of estimators. More recently, Moka et al. [2019] has
looked into the special case of formulating non-negative estimators
for the reciprocal.
4 ESTIMATION AND CONVERGENCE
Up until now, all our formulations have been defined with respect
to expected values, but to use them in practice we need to turn

```
them into estimators. In this section we develop a recipe (Recipe 1)
```

for creating debiased and consistent estimators for any problem

```
in the form of Eq. (2). Assuming we have already chosen a valid
```

```
representation for Δ𝑗 by using Eq. (4) or Eq. (12), all that remains to
```

complete step 1 is to construct a primary and secondary estimator.
Recipe 1. A recipe for creating debiased and consistent estimators for

```
problems in the form of Eq. (2).
```

```
1 Construct estimators: Choose Δ𝑗 representation respecting Eq. (1),
```

```
build primary (Sec. 4.1) and secondary (Sec. 4.2) estimators.
```

2 Determine rates: Determine asymptotic rates of Δ𝑗 , variance
V[ ⟨Δ𝑗 ⟩], and cost C[ ⟨Δ𝑗 ⟩], as 𝑗 → ∞.

```
3 Derive PMF: Insert rates into Eq. (18); check if resulting PMF 𝑝 ( 𝑗)
```

can be normalized. If not, skip to step 5 .

```
4 Verify finite work-normalized variance: Insert 𝑝 ( 𝑗) into esti-
```

mator ⟨𝐼 ⟩1 and confirm the work C[ ⟨𝐼 ⟩1 ] is finite. If yes, work-
normalized variance is finite, done.

```
5 Build unbiased infinite-variance estimator: Fix 𝑝 ( 𝑗) to some-
```

thing reasonably normalizable, set the growth rate of C[ ⟨𝑘𝑗 ⟩] suffi-
ciently high while still remaining finite to decrease the rate at which
V[ ⟨𝑘𝑗 ⟩] approaches infinity. Evaluate secondary estimator. If noise
is acceptable, done.
6 Build consistent progressive estimator: Convert the secondary
estimator into a consistent progressive estimator, and reparameterize
Δ𝑘 such that V[ ⟨Δ𝑘 ⟩] behaves asymptotically strictly sublinearly
w.r.t. 𝑘, done.
4.1 Primary estimators
Based off the nomenclature introduced by Georgiev et al . [2019], we

```
consider two approaches for building primary estimators for Eq. (2).
```

Single-term estimator. One approach is to randomly choose one

```
term 𝑗 of the bias sum (2) according to some probability mass func-
```

```
tion (PMF) 𝑝 ( 𝑗), then combine it with the biased estimate ⟨𝐼 (𝑘)⟩:
```

```
⟨𝐼 ⟩𝑘1 = ⟨𝐼 (𝑘)⟩ + ⟨𝐵(𝑘)⟩ = ⟨𝐼 (𝑘)⟩ + ⟨Δ𝑗 ⟩𝑝 ( 𝑗) . (14)
```

Prefix-sum estimator. Alternatively, having sampled a term 𝑗 from

```
𝑝 ( 𝑗) we could evaluate the prefix of all terms up to 𝑗:
```

```
⟨𝐼 ⟩𝑘1 = ⟨𝐼 (𝑘)⟩ + ⟨𝐵(𝑘)⟩ = ⟨𝐼 (𝑘)⟩ +
```

𝑗Õ
𝑖=𝑘
⟨Δ𝑖 ⟩

```
𝑃 ( 𝑗 ≥ 𝑖) , (15)
```

```
where 𝑃 ( 𝑗 ≥ 𝑖) is the cumulative mass function (CMF) giving the
```

probability for sampling 𝑗 ≥ 𝑖.
Note that we could create analogous estimators for the continuous

```
formulation (10) by making 𝑝 ( 𝑗) a probability density function, and
```

```
using a “prefix integral” instead of a sum in Eq. (15).
```

4.2 Secondary estimator
To ensure that our approach converges to the sought value 𝐼 , we
form a secondary estimator,
⟨𝐼 ⟩𝑁 = 1𝑁
𝑁Õ
𝑖=1

```
⟨𝐼 ⟩𝑘𝑖1 , (16)
```

which averages 𝑁 independent instances of the primary estimator.
Typically 𝑘𝑖 = 𝑘 will be a constant, meaning the secondary estima-

```
tor Eq. (16) will take the average of 𝑁 independent and identical
```

evaluations of the primary estimator. However, no matter how 𝑘𝑖

```
is assigned, Eq. (16) will always be unbiased because the primary
```

estimator is unbiased for any starting 𝑘. For example, an unbiased
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:5

```
progressive estimator could be constructed from Eq. (16) by setting
```

𝑘𝑖 = 𝑖. This completes step 1 .
4.3 Estimation under finite variance
Steps 2 , 3 , and 4 involve determining if we can formulate a
primary estimator with finite variance, and if so, how to do so as
optimally as practically possible.
Since our primary estimators have the correct expected value
by construction, then as long as they have finite variance, the cen-
tral limit theorem tells us that the secondary estimator ⟨𝐼 ⟩𝑁 will

```
converge to 𝐼 at an asymptotic rate of V[⟨𝐼 ⟩𝑁 ] = O(1/𝑁 ). The con-
```

stant factor in this asymptotic rate, however, will depend heavily

```
on the construction of ⟨Δ𝑗 ⟩ and the choice of 𝑝 ( 𝑗). When a primary
```

estimator has finite variance, the ideal strategy would be to choose

```
⟨Δ𝑗 ⟩ and 𝑝 ( 𝑗) to minimize its work-normalized variance:
```

arg min

```
𝑝 ( 𝑗)
```

```
V[⟨𝐼 ⟩1] C[⟨𝐼 ⟩1] , (17)
```

where C[⟨𝐼 ⟩1] is its expected cost. Rhee [2013] derived expressions

```
for the work-normalized variance optimal 𝑝 ( 𝑗). Unfortunately, this
```

is primarily of theoretical interest since it requires knowledge of

```
not only V[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)] and C[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)] (which are unfortunately not
```

```
available for most problems in graphics), it also requires knowledge
```

of 𝐼 , the very quantity we are trying to estimate.

```
A more pragmatic approach would be to derive a 𝑝 ( 𝑗) which
```

```
simply minimizes variance, V[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)], and then check whether
```

the resulting estimator also has finite work-normalized variance. In
Appendix A, we prove that for both continuous and discrete forms

```
of single-term estimation (14), the variance-optimal 𝑝 ( 𝑗) is
```

```
𝑝 ( 𝑗) ∝
```

√

```
V[⟨Δ𝑗 ⟩] + (Δ𝑗)2. (18)
```

```
This matches the variance-optimal 𝑝 ( 𝑗) that Rhee [2013] derived
```

```
for the case of the discrete telescoping series (12) . Later, Blanchet
```

```
et al. [2015] showed that this 𝑝 ( 𝑗) also applies to the general Taylor
```

```
series formulation (4).
```

```
Compared to Eq. (17), it is more feasible to apply Eq. (18) since
```

even though we may not know V[⟨Δ𝑗 ⟩] or Δ𝑗 exactly, we can of-
ten obtain their asymptotic rates 2 and use them to derive 3 an

```
asymptotically optimal 𝑝 ( 𝑗). If 𝑝 ( 𝑗) is not normalizable then our
```

```
estimator will not have finite work-normalized variance. If 𝑝 ( 𝑗) is
```

```
normalizable, we need to additionally verify 4 that C[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)] is
```

finite. If not, then modifying the estimator to have finite work for
practical implementations might still result in infinite variance.
4.4 Estimation under infinite variance
Since our primary estimators have the correct expected value by
construction, the weak law of large numbers guarantees that the

```
secondary estimator (16) will converge in probability to 𝐼 as 𝑁
```

increases. Remarkably, this is the case even if the variance of the
primary estimator is infinite, as we will see for the case of debiased

```
photon mapping; however, the convergence rate may be slower
```

```
than O(1/𝑁 ) since the central limit theorem does not apply. We
```

demonstrate this in Fig. 3 for the case of estimating the integral of
a simple function with a controllable amount of variance. Even in
cases where the primary estimator has infinite variance, a secondary
0.02 0.04 0.06 0.08 0.10𝑥
20
40
60
80
100
1
𝑥𝛼
𝛼 = 0.9
𝛼 = 0.8
𝛼 = 0.6
𝛼 = 0.4
215 217 219 221Secondary samples
2−3
2−1
Relative MAE
-0.1-0.2
-0.3-0.4
-0.5𝛼 = 0.9𝛼 = 0.8
𝛼 = 0.6
𝛼 = 0.4

```
Fig. 3. The integral ∫ 101𝑥𝛼 d𝑥 (left) provides a useful test case for finite vs.
```

infinite variance primary estimators. The integral takes on a closed-form

```
value of (1 −𝛼)−1 for any 𝛼 ∈ (0, 1), but the variance of a primary estimator
```

using uniform sampling is finite only for 𝛼 < 0.5. For 𝛼 ≥ 0.5 the variance

```
is infinite, leading to slower convergence of a secondary estimator (right).
```

estimator will converge in expectation, but at a slower rate compared
to when variance is finite.
We can choose to formulate either an unbiased estimator 5 , or
formulate a consistent estimator 6 . The consistent estimator will
be biased, but the unbiased estimator will exhibit higher variance.
Unbiased estimation. When utilizing an unbiased primary estima-
tor in the case of infinite variance, the convergence rate is heavily

```
influenced by the rate at which V[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)] approaches infinity.
```

We could create practical estimators by choosing the estimators’

```
parameters such that V[ ⟨Δ𝑗 ⟩/𝑝 ( 𝑗)] approaches infinity as slowly as
```

reasonably possible.
Selecting an optimal parameter configuration for such an esti-
mator may be challenging, so we instead take a more pragmatic

```
approach: For many applications V[⟨Δ𝑗 ⟩] is inversely related with
```

```
C[⟨Δ𝑗 ⟩]; for example, in photon mapping, tracing more photons
```

reduces its variance. By increasing the rate at which C[⟨Δ𝑗 ⟩] grows
with 𝑗, we also reduce the rate at which V[⟨Δ𝑗 ⟩] increases with 𝑗.
This way we may achieve workable convergence rates for debiased
estimators while still maintaining finite cost C[⟨𝐼 ⟩1].
Consistent estimation. Although debiasing is still possible in the
case of infinite variance, the noise which arises from unbiased es-
timators with slower convergence may not be acceptable in all
applications. In these cases, we can formulate an alternative consis-
tent progressive estimator, similar to progressive photon mapping,
which trades noise for bias. In Appendix E, we show that a consis-

```
tent progressive estimator can be derived directly from Eq. (16) by
```

```
choosing 𝑘𝑖 = 𝑖 and never evaluating 𝐵(𝑘).
```

This consistent progressive formulation is identical to the one
used by progressive photon mapping, so we can utilize the analysis
of prior work to construct efficient consistent estimators. First, we
take our estimator from 5 and reparameterize 𝑘𝑖 such that the

```
primary estimators’ variance 𝑉 (𝑘𝑖 ) = V[⟨𝐼 (𝑘𝑖 )⟩] behaves asymp-
```

```
totically strictly sublinearly w.r.t. 𝑖. That is, 𝑉 (𝑘𝑖 ) is allowed to
```

increase, but not faster than 𝑖 itself, which ensures that the variance
of ⟨𝐼 ⟩c𝑁 vanishes. The parameterization that maximizes that estima-

```
tor’s error convergence rate is the one that achieves O(𝑉 (𝑘𝑖 )) =
```

```
𝑘O (𝐵2 (𝑘𝑖 )).
```

Once we have constructed a consistent progressive estimator, we
have completed 6 , and now we can apply our recipe to formulate
unbiased estimators for novel problems.
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:6 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz
-10
-5
0
25
50

```
𝐼 (𝑘) Debiased Reference
```

Fig. 4. Debiased finite differences with respect to the roughness of a metallic
object in a scene where the main light source is partially obstructed. Our

```
method debiases the initial 𝐼 (𝑘) (ℎ = 0.005) to match the reference (right)
```

```
which was rendered using (ℎ = 0.0001).
```

5 APPLICATIONS
In this section, we show applications of our theory to common
problems in graphics. We show several novel applications, namely

```
unbiased/progressive finite differences (Sec. 5.1), unbiased non-
```

```
exponential transmittance (Sec. 5.2), as well as unbiased photon
```

```
mapping and unbiased progressive photon mapping (Sec. 5.3). We
```

implemented all methods in the PBRT renderer [Pharr et al. 2016].
5.1 Finite differences
As an example of directly applying Recipe 1 to estimate a novel

```
problem, consider computing the derivative of an integral 𝐹 (𝑥) =∫
```

```
Ω 𝑓 (𝑥, 𝑦) d𝑦 with respect to the parameter 𝑥:
```

```
𝐼 B 𝜕𝐹 (𝑥)𝜕𝑥 = 𝜕𝜕𝑥
```

∫

```
Ω𝑓 (𝑥, 𝑦) d𝑦. (19)
```

```
For example, the function 𝑓 (𝑥, 𝑦) could represent the contribution
```

of a light path 𝑦 in a scene parameterized by 𝑥. Note that the domain
of integration Ω may depend on 𝑥.

```
Devising ways to estimate Eq. (19) efficiently and accurately is the
```

main goal of differentiable rendering. Even though finite differences
are not a practical approach for estimating high-dimensional deriva-
tives in an inverse rendering context, they remain a common base-
line for validating new differentiable rendering techniques, thanks
to their generality and ease of implementation. Unfortunately, since
finite differences are biased, such “ground truth”-baseline compar-
isons remain imperfect. Following all steps outlined in Recipe 1, we
will derive both unbiased and consistent alternatives to finite differ-
ences, which could serve as more accurate ground-truth techniques
for validation of future differentiable rendering methods.

```
We first denote the (biased) finite difference approximation of
```

```
Eq. (19) as 𝐼 (𝑘),
```

```
𝜕𝐹 (𝑥)
```

```
𝜕𝑥 ≈ 𝐼 (𝑘) B
```

1
ℎ𝑘

```
(∫
```

```
Ω1𝑓 (𝑥 + ℎ𝑘 , 𝑦1) d𝑦1 −
```

∫

```
Ω2𝑓 (𝑥, 𝑦2) d𝑦2
```

```
)
```

```
, (20)
```

where 𝑘 maps to a finite-difference step size ℎ𝑘 , and Ω1 ≠ Ω2 if the
integration domain depends on 𝑥. By the definition of a derivative,

```
this formulation satisfies Eq. (1) as long as ℎ𝑘 → 0 as 𝑘 → ∞; we
```

use ℎ𝑘 ∝ 2−𝑘 .
We can now formulate unbiased finite differences using our

```
telescoping-series formulation (12) as
```

```
𝐼 = 𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘
ΔFD𝑗

```
𝐵 (𝑘)
```

```
, where ΔFD𝑗 = 𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗). (21)
```

```
We use standard Monte Carlo rendering to form ⟨𝐼 ( 𝑗)⟩ where we
```

choose to maximally correlate the two integral estimates, and we

```
use a single-term estimate of Eq. (21). This completes step 1 .
```

```
Unbiased estimation. For the cases where 𝑓 (𝑥, 𝑦) is finite, contin-
```

uously differentiable with respect to 𝑥, and Ω does not depend on
𝑥, we show in Appendix D.1 how to form an estimator ⟨ΔFD𝑗 ⟩ with
finite variance and derive the asymptotic rates for Δ𝑗 and V[⟨Δ𝑗 ⟩],

```
completing step 2 . Inserting these formulations into Eq. (18), we ar-
```

```
rive at the variance optimal 𝑝 ( 𝑗) ∝ 2−𝑗 to utilize in our single-term
```

primary estimator, completing step 3 . Since the cost of evaluating
finite differences is constant, we have arrived at an unbiased esti-
mator with finite work-normalized variance 4 . Figure 4 shows an
example of differentiating with respect to material roughness. Since
Ω is not dependent on 𝑥 for this case, we choose to fully correlate
paths by always performing BSDF importance sampling using the
same BSDF and evaluate all integral estimates simultaneously.
SceneScene
-0.003 -0.0015 0.00 0.05 0.102
7 29 211 213
progressive iteration
2−24
2−22
MSE
ReferenceReference 20 iter.20 iter. ReferenceReference 24 iter.24 iter. ReferenceReference 217 iter.217 iter.
Fig. 5. We show the convergence of our progressive finite differences for
evaluating the derivative of ambient occlusion on a plane by a sphere as the
sphere moves upwards, whose analytic ground truth derivative is known.
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:7
-1.0
-0.5
0.0
0.5
1.0
24 iterations24 iterations 28 iterations28 iterations 213 iterations213 iterations
Fig. 6. Convergence of progressive finite differences w.r.t. moving a point
light source to the right in a scene with visibility discontinuities. Each
progressive iteration uses 16 samples/pixel.

```
Consistent estimation. If 𝑓 (𝑥, 𝑦) is not continuous with respect to
```

```
𝑥 (for example, when 𝑥 impacts visibility), then the variance of the
```

primary estimator, V[⟨𝐼 ⟩𝑘1 ], can become infinite. For this case, we
skip to step 5 . Through experimentation we found the unbiased
estimators for the infinite variance case to be too noisy in practice,
so instead we continue to step 6 and formulate a consistent es-
timator. For the case where Ω does not depend on 𝑥, we show in
Appendix D.2 that finite differences are biased because they blur the
true derivatives with a box kernel. This allows us to draw an analogy
to progressive photon beams to form a progressive finite difference
estimator with the same theoretical convergence guarantees for the
ideal case. The estimators will still converge for the discontinuous
case, however their convergence rates will be slower. In Fig. 5, we
verify that this progressive estimator is consistent on an ambient

```
occlusion scene with a close-form ground truth; in Fig. 6, we show
```

a more complex example in a scene with obvious discontinuities,
showing how progressive iterations of our estimator reduce the blur-
ring of finite differences in much the same way as in progressive
photon beams.
5.2 Non-exponential transmittance
At its core, computing transmittance in volumetric rendering in-

```
volves estimating a function of expectations (3) 𝐼 B 𝑔(𝐹 ) where
```

𝐹 is the optical depth integral along a ray. Estimating 𝐹 numeri-
cally in heterogeneous media leads to bias when passed through
the transmittance function 𝑔. In classical radiative transport, the

```
transmittance is simply the exponential, 𝑔(𝐹 ) B e−𝐹 , but recent
```

```
non-exponential formulations [Bitterli et al . 2018; Jarabo et al . 2018]
```

allow for using any monotonically decreasing function 𝑔 that starts

```
at 𝑔(0) = 1.
```

1 3 5 7 9 11 13 15
2−24
2−15
2−6
Variance
1 3 5 7 9 11 13 15
2−11
2−6
2−1
Work normalized variance
uncorrelated
correlated
Fig. 7. Correlating samples when estimating ⟨ΔRM𝑗 ⟩ can have a dramatic
impact on convergence. Here 𝐼 B e

```
∫ −𝑓 (𝑥 ) d𝑥
```

```
where 𝑓 (𝑥) is some random
```

noise and the integral is estimated with a 2𝑗 -sample Monte Carlo estimator.

```
The graph in red shows the variance (left) and work-normalized variance
```

```
(right) with uncorrelated evaluation ⟨Δ𝑗 ⟩ = ⟨𝐼 ( 𝑗 + 1) ⟩ − ⟨𝐼 ( 𝑗) ⟩, while in
```

```
blue we show the improvement when evaluating ⟨Δ𝑗 ⟩ = ⟨𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗) ⟩
```

using Blanchet and Glynn’s [2015] technique for correlating samples.
Unfortunately, estimation of such non-exponential transmittance
still lags behind traditional transport because most available tech-

```
niques [Georgiev et al . 2019; Kettunen et al . 2021; Kutz et al. 2017;
```

Novák et al . 2014] rely on the exponential assumption. This leaves

```
only raymarching (biased) or regular tracking (slow) as possible
```

techniques for general forms of transmittance 𝑔. Luckily, since trans-
mittance is a function of expectations, it is readily debiasable using

```
our framework with both Eqs. (4) and (12).
```

Telescoping series for general transmittance. The telescoping se-

```
ries formation (12) allows us—for the first time—to form unbiased
```

estimators for general transmittance functions as

```
𝐼 B 𝑔(𝐹 ) = 𝐼 (𝑘)
```

biased transmittance estimate

-

```
bias 𝐵 (𝑘)
```

∞Õ
𝑗=𝑘

```
ΔRM𝑗 , with ΔRM𝑗 = 𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗). (22)
```

```
We use 𝐼 (𝑘) to denote the biased evaluation of transmittance 𝑔 where
```

we use ray marching with a monotonically decreasing sequence of

```
step sizes to estimate 𝐹 (though any numerical estimation technique
```

```
for 𝐹 is admissible as long as it ensures consistency (1) in the limit
```

```
as 𝑘 → ∞).
```

```
We form a single-term estimator ⟨𝐼 ⟩𝑘1 of Eq. (22) using a geometric
```

```
PMF 𝑝 ( 𝑗) = 𝑟 (1 − 𝑟 ) 𝑗 with 𝑟 = 0.65, as recommended by Blanchet
```

```
and Glynn [2015] for applying Eq. (12) to smooth functions of ex-
```

pectations. We set the ray marching step size to 𝑠𝑗 ∝ 2−𝑗 . Doubling
the number of ray marching steps this way allows for dramatic
sample reuse and variance reduction when estimating ⟨ΔRM𝑗 ⟩ since

```
we can evaluate both ⟨𝐼 ( 𝑗 + 1)⟩ and ⟨𝐼 ( 𝑗)⟩ simultaneously with a
```

shared set of ray marching samples. In fact, we can reduce variance
further [Blanchet and Glynn 2015] by splitting the 𝑁 samples from

```
⟨𝐼 ( 𝑗 + 1)⟩ into two groups and averaging two separate estimators
```

```
for ⟨𝐼 ( 𝑗)⟩ with 𝑁 /2 samples each. We show in Fig. 7 that these mea-
```

sures have a profound impact on not just the variance V[⟨ΔRM𝑗 ⟩],
but also its asymptotic convergence rate.
In Fig. 8 we demonstrate this estimator on the WDAS cloud scene
using the two-parameter Davis and Mineev-Weinstein transmittance
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:8 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz
ExponentialExponential
𝐶 = 1.0, 𝛽 = 0.25𝐶 = 1.0, 𝛽 = 0.25
𝐶 = 2.0, 𝛽 = 0.50𝐶 = 2.0, 𝛽 = 0.50
𝐶 = 3.0, 𝛽 = 0.75𝐶 = 3.0, 𝛽 = 0.75
26 27 28 29 210 211 212pixel samples2
−15
2−13
2−11
2−9
2−7
MSE
exponential
𝛽 = 0.25, 𝐶 = 1.0
𝛽 = 0.50, 𝐶 = 2.0
𝛽 = 0.75, 𝐶 = 3.0

```
Fig. 8. Illustration of our telescoping-based debiased ray-marching (22).
```

The split image shows classical transmittance as well as non-exponential
transmittance with three different choices for 𝐶 and 𝛽. The plot shows the
convergence of four select pixels towards a regular-tracked ground truth.
model,

```
𝑔(𝐹 ) B
```

```
(
```

1 + 𝐹 𝛽𝐶1+𝛽

```
)− 𝐹 1−𝛽𝐶1+𝛽
```

```
, (23)
```

for a variety of settings of 𝛽 and 𝐶 which together control the
shape of the transmittance curve. We compare our results to regular
tracking, confirming that our estimator is unbiased, and that the

```
variance V[⟨𝐼 ⟩𝑁 ] falls off at the expected O(1/𝑁 ) convergence rate.
```

Taylor series for pink-noise transmittance. We can also apply the

```
Taylor series formulation to Eq. (23). For arbitrary values of 𝛽, we
```

found that the complexity of the derivative terms in the Taylor
expansion grows exponentially for increasing values of 𝑗. However,

```
for the special case of “pink-noise” (𝛽 = 1), Eq. (23) simplifies to
```

```
𝑔(𝐹 ) B
```

```
(
```

1 + 𝐹𝐶2

```
)− 1𝐶2
```

```
, (24)
```

```
which admits a compact Taylor series formulation (4):
```

```
𝐼 B 𝑔(𝐹 ) =
```

𝑘−1Õ
𝑗=0
Δpink𝑗

```
𝐼 (𝑘)
```

- ∞Õ
  𝑗=𝑘
  Δpink𝑗

```
𝐵 (𝑘)
```

, where

```
Δpink𝑗 = (𝛼 − 𝐹 )
```

𝑗
𝑗!

```
(
```

1 + 𝛼𝐶2

```
) −1𝐶2 −𝑗 𝑗−1Ö
```

𝑖=1

```
(
```

1 + 𝑖𝐶2

```
)
```

.

```
(25)
```

```
We create a prefix-sum primary estimator of Eq. (25) by defining
```

```
the PMF 𝑝 ( 𝑗) indirectly via Russian roulette probabilities:
```

```
𝑃acc ( 𝑗) = 1 + ( 𝑗 − 1)𝐶
```

2

```
𝑗 , 𝑝 ( 𝑗) = (1 − 𝑃acc ( 𝑗))
```

𝑗−1Ö
𝑖=0

```
𝑃acc (𝑖) . (26)
```

Since this is independent of both the expansion point 𝛼 and any
optical depth evaluation, ⟨𝐹 ⟩, we can take advantage of all the same
variance reduction techniques that Kettunen et al. [2021] introduced
for exponential transmittance. We use uniformly jittered regular

```
samples with a fixed step-size (0.2) to estimate ⟨𝐹 ⟩. We set 𝑘 = 3,
```

```
and choose to evaluate the bias only a portion (𝑃 = 0.1) of the time
```

which reduces the cost while slightly increasing the variance of the
estimator.

```
In Fig. 9 we compare both our Taylor series (25) and telescoping
```

```
series (22) estimators against prior techniques for unbiased estima-
```

tion of both pink-noise- and exponential-transmittance functions.

```
Bitterli et al . [2018] showed that ratio tracking (or any existing ex-
```

```
ponential transmittance estimator) can be reused for pink noise by
```

first sampling a multiplicative factor 𝛾 from a gamma distribution,
and then estimating exponential transmittance in a medium with
its density scaled by 𝛾. We also apply this trick to Kettunen et al .
[2021]’s more recent unbiased ray marching technique, to allow it to
handle both exponential and pink-noise transmittance. As shown in
Fig. 9, our estimators consistently outperform these prior methods,
sometimes reducing RMSE by a factor of 10× at equal cost.
In our full implementation [Misso et al . 2022] we additionally
provide a novel estimator akin to Georgiev et al .’s [2019] pseries-
cumulative estimator but for pink-noise and include more compar-
isons in canonical pink-noise and exponential media for all our
estimators.
5.3 Photon mapping
Photon mapping is the most practical algorithm for rendering com-
plex caustic effects. It emits photons from light sources which are
then used to compute the radiance at a point in the scene via den-
sity estimation. However, density estimation yields a result with

```
bias dependent on the radius 𝑟 of the density kernel used; the bias
```

vanishes as the radius approaches zero. Note that while an unbiased
formulation of photon mapping exists [Qin et al . 2015], it does not
handle purely specular caustics.

```
We denote the (biased) expectation of the photon mapping radi-
```

```
ance estimate as 𝐼 (𝑘), where 𝑘 maps to a monotonically decreasing
```

sequence of radii 𝑟𝑘 used for density estimation. We can create a

```
telescoping-series formulation (12) for the problem as
```

```
𝐼 = 𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘
ΔPM𝑗

```
𝐵 (𝑘)
```

```
, where ΔPM𝑗 = 𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗), (27)
```

which fully debiases photon mapping, even in the presence of caus-

```
tics. In essence, Eq. (27) represents the bias as consecutive differences
```

```
of kernels with monotonically decreasing radii (Fig. 10).
```

By utilizing the known convergence rates of progressive photon
mapping, we show in Appendix C that it is not possible for both
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:9
𝐶 = 0.3𝐶 = 0.3 𝐶 = 0.8𝐶 = 0.8

```
RMSE: 4.1e-3RMSE: 4.1e-3
```

𝐶 = 0.3𝐶 = 0.3

```
RMSE: 4.2e-3RMSE: 4.2e-3
```

```
RMSE: 4.3e-3RMSE: 4.3e-3
```

Exponential

𝐶
= 0
.3

```
RMSE: 14.6e-3RMSE: 14.6e-3
```

```
RMSE: 6.4e-3RMSE: 6.4e-3
```

```
RMSE: 18.3e-3RMSE: 18.3e-3
```

```
RMSE: 16.4e-3RMSE: 16.4e-3
```

```
RMSE: 3.3e-3RMSE: 3.3e-3
```

𝐶 = 0.8𝐶 = 0.8

```
RMSE: 2.6e-3RMSE: 2.6e-3
```

```
RMSE: 4.3e-3RMSE: 4.3e-3
```

Exponential

𝐶
= 0
.8

```
RMSE: 33.9e-3RMSE: 33.9e-3
```

```
RMSE: 6.4e-3RMSE: 6.4e-3
```

```
RMSE: 25.0e-3RMSE: 25.0e-3
```

```
RMSE: 16.4e-3RMSE: 16.4e-3
```

```
Reference Pink-Taylor (ours) Telescoping (ours) Kettunen et al. [2021] Bitterli et al. [2018]
```

```
Fig. 9. Comparing a variety of transmittance estimators for a non-exponential medium with the Davis and Mineev-Weinstein transmittance model Eq. (23) for
```

```
two different values of 𝐶 for an equal number of extinction calls (1.2e8 for 𝐶 = 0.3, 0.8, and 1.0e8 for exponential). The three estimators on the right can be
```

used as estimators for exponential transmittance, so we also include inset comparisons for an exponential medium at the top of their respective insets. RMSE
values are measured across the entire image.
Photon mappingPhoton mapping Negative biasNegative bias
EV+1EV+1
EV+1EV+1

```
Positive biasPositive biasUnbiased photon mapping (ours)Unbiased photon mapping (ours)
```

−

- =
  Fig. 10. Decomposition of our unbiased photon mapping into the sum of
  a biased estimate and a bias term. We separate the bias into positive and
  negative parts for ease of visualization.

```
3 and 4 to hold, i.e., we cannot debias Eq. (27) with finite work-
```

normalized variance. However, unbiased secondary estimators still
converge by the law of large numbers.
Unbiased photon mapping. We formulate unbiased photon map-

```
ping via a single-term primary estimator (14) , and a secondary
```

```
estimator (16) with 𝑘𝑖 = 𝑘 for 5 . We use a cone kernel and fully
```

correlate all kernel evaluations, in essence by estimating ⟨ΔPM𝑗 ⟩ B

```
⟨𝐼 ( 𝑗 + 1) − 𝐼 ( 𝑗)⟩ instead of ⟨𝐼 ( 𝑗 + 1)⟩−⟨𝐼 ( 𝑗)⟩. We use 𝑝 ( 𝑗) ∝ O( 𝑗𝛼−2),
```

```
and set the number of global photons to O( 𝑗1−𝑐𝛼 ) where 𝑐 = 1.001
```

and 𝛼 = 2/3. Compared to prior progressive photon mapping meth-

```
ods, our debiased photon mapping trades bias (i.e., blurring) for
```

```
noise (Fig. 11).
```

Unbiased progressive photon mapping. We can also debias progres-
sive photon mapping by making a small change in the secondary

```
estimator (16): setting 𝑘𝑖 = 𝑖 instead of having it constant to com-
```

plete 5 . This is equivalent to progressive photon mapping, with
an additional estimation of the bias of each progressive iteration. If
we instead continued from 5 and performed 6 , we would end up
with prior work’s consistent progressive photon mapping.
In Fig. 12, we compare convergence rates of our debiased methods
and prior progressive photon mapping in terms of emitted photons.
6 CONCLUSION
We have introduced a general framework for formulating unbiased
and consistent estimators from biased ones as well as provided a
general recipe for applying our framework to novel problems. We
have shown how specializations of these techniques have already
appeared in graphics for reciprocal and classical transmittance esti-
mation, and how to apply them to a broader class of problems. We
have introduced unbiased progressive estimation and have shown
how prior biased but consistent formulations, i.e. progressive photon
mapping, can be obtained from our unbiased formulation as a means
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:10 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz

```
Progressive photon mapping Unbiased photon mapping (ours)
```

```
Fig. 11. Compared to progressive photon mapping (with 𝛼 = 2/3) at equal
```

```
number (3.3e10) of emitted photons, our unbiased photon mapping trades
```

```
blurring (i.e., bias) for noise.
```

of trading noise for bias when unbiased estimation leads to infinite
variance. Using our framework, we have introduced a debiased ray-
marching approach which is the first unbiased estimator to support
general non-exponential transmittance. We have introduced the first
unbiased formulation for photon mapping and progressive photon
mapping which supports caustics. We have also shown how to make
finite differences unbiased for smooth functions, and formulated a
consistent estimator in the presence of discontinuities.
Discussion and future work
The primary estimators we have used rely on either a Taylor series

```
(4) or telescoping series (12) expansion, so a reasonable question
```

to ask is which one should be used when they both apply? We
have found this to be extremely problem-dependent. For example,
some of the variance reduction techniques introduced by Kettunen
et al. [2021] for transmittance estimation cannot be utilized for
reciprocal estimation due to its singularity, causing the optimal
design decisions for reciprocal estimation to differ from problems
akin to transmittance. While an extensive comparative analysis
could prove invaluable in guiding such design decisions in future
work, there are some clear trade-offs between the two algorithms
that are already apparent from our investigations.
The telescoping series performs best when implemented as a

```
global algorithm which combines evaluations of 𝐼 (𝑘) as a post pro-
```

cess. This requires re-structuring rendering algorithms to integrate
multiple values separately and correlate entire paths for maximum
performance. The Taylor series is applicable only to smooth func-
tions of expectations, making it less general, but more self-contained
and easier to maintain, compared to the telescoping series. By uti-
lizing relatively large initial 𝑘’s and each formulations’ respective
variance reduction techniques, both formulations can reach compa-
rably low work-normalized-variances.
In addition to looking into optimal estimation configurations for
specific applications, there are ample opportunities for exploring

```
232 233 234 235 236 237cost (photons emitted)
```

2.5e-3
1.2e-3
6.2e-4
Mean absolute error
PPM
1.2e+0
6.1e-1
3.0e-1
Unbiased PM
Unbiased PPM
Fig. 12. We show the convergence of the mean absolute difference of our un-
biased photon mapping and unbiased progressive photon mapping against
progressive photon mapping for a canonical scene containing only a plane
and a point light source while measured from a single location for equal
cost. The convergence rates between progressive photon mapping and our
unbiased photon mapping are similar.

```
Taylor-cumul. (ours) Bernoulli Trials Telescoping (ours)
```

```
Fig. 13. Preliminary equal-time (10 minutes) results showing a potential ap-
```

plication in formulating unbiased estimation for specular manifold sampling

```
[Zeltner et al . 2020] (i.e. reciprocal estimation). Our Taylor-series estima-
```

```
tor (left), based on the pseries-cumulative estimator estimator of Georgiev
```

et al . [2019], performs similarly to Bernoulli trials. Making our telescoping-

```
series estimator (right) competitive requires further investigation.
```

the full potential of our framework. Most notably, the current state
of the art for estimating the reciprocal of a probability is a Bernoulli

```
trial estimator (Fig. 13). While we found some of our estimators can
```

match the performance of Bernoulli trials, we believe further work
could use our framework to derive even more efficient estimators.
Many algorithms in graphics use Russian roulette to probabilisti-
cally account for an infinite series in finite time. This is just an in-

```
stance of Eq. (12)’s telescoping debiasing. Russian roulette, however,
```

does not typically choose a selection PMF a priori. The effective PMF
ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:11
is rather a consequence of each Russian roulette decision, which can
notably adapt to local information on the fly. So far, our applications

```
of Eq. (12) have only explored specifying a single global PMF. In the
```

case of path tracing truncation, this would be like specifying the
probability of sampling specific length paths without knowing the
reflectivity of the surfaces encountered along the paths. Exploring
and constructing estimators which exploit local information in Rus-
sian roulette and weight windows [Vorba and Křivánek 2016] could
be a promising avenue for future work.
The Volterra formulation for transmittance has been shown to
encompass all of the prior tracking-based transmittance estima-
tors, which have analogous free-flight distance sampling routines
[Georgiev et al . 2019]. Originally, this formulation was derived in
a manner which was tied to the definition of classical exponen-
tial transmittance. Reformulating this directly as an initial value

```
problem (9,13) opens the possibility to more easily derive unbiased
```

free-flight distance sampling routines for non-exponential media.
ACKNOWLEDGMENTS
The cloud model in Fig. 8 is from Walt Disney Animation Studios.
The scenes for Fig. 2, Fig. 4 and Fig. 10 were based off of scenes from
Bitterli [2016]. This work was generously supported by NSF awards
1812796 and 1844538, a Neukom Institute CompX faculty grant, and
a Facebook PhD fellowship.
REFERENCES

```
Sai Praveen Bangaru, Tzu-Mao Li, and Frédo Durand. 2020. Unbiased Warped-AreaSampling for Differentiable Rendering. ACM Transactions on Graphics (Proceedings
```

```
of SIGGRAPH Asia) 39, 6 (Nov. 2020), 245:1–245:18. https://doi.org/10/gj32skBenedikt Bitterli. 2016. Rendering resources. https://benedikt-bitterli.me/resources/.
```

Benedikt Bitterli, Srinath Ravichandran, Thomas Müller, Magnus Wrenninge, Jan Novák,Steve Marschner, and Wojciech Jarosz. 2018. A Radiative Transfer Framework for

```
Non-Exponential Media. ACM Transactions on Graphics (Proceedings of SIGGRAPHAsia) 37, 6 (Nov. 2018), 225:1–225:17. https://doi.org/10/gfz2cm
```

Jose H. Blanchet, Nan Chen, and Peter W. Glynn. 2015. Unbiased Monte Carlo Compu-tation of Smooth Functions of Expectations via Taylor Expansions. In 2015 Winter

```
Simulation Conference (WSC). 360–367. https://doi.org/10/ggr94pJose H. Blanchet and Peter W. Glynn. 2015. Unbiased Monte Carlo for Optimization and
```

```
Functions of Expectations via Multi-Level Randomization. In 2015 Winter SimulationConference (WSC). 3656–3667. https://doi.org/10/ggr94h
```

T. E. Booth. 2007. Unbiased Monte Carlo Estimation of the Reciprocal of an Integral.Nuclear Science and Engineering 156, 3 (July 2007), 403–407. https://doi.org/10/
gfzq76Jérémi Dauchet, Jean-Jacques Bezian, Stéphane Blanco, Cyril Caliot, Julien Charon,
Christophe Coustet, Mouna El Hafi, Vincent Eymet, Olivier Farges, Vincent Forest,Richard Fournier, Mathieu Galtier, Jacques Gautrais, Anaïs Khuong, Lionel Pelissier,

```
Benjamin Piaud, Maxime Roger, Guillaume Terrée, and Sebastian Weitz. 2018. Ad-dressing Nonlinearities in Monte Carlo. Scientific Reports 8, 1 (Dec. 2018), 13302.
```

```
https://doi.org/10/gd76pcAnthony B. Davis and Mark B. Mineev-Weinstein. 2011. Radiation Propagation in
```

```
Random Media: From Positive to Negative Correlations in High-Frequency Fluctu-ations. Journal of Quantitative Spectroscopy and Radiative Transfer 112, 4 (March
```

```
2011), 632–645. https://doi.org/10/fgxnc4Iliyan Georgiev, Jaroslav Křivánek, Tomáš Davidovič, and Philipp Slusallek. 2012. Light
```

```
Transport Simulation with Vertex Connection and Merging. ACM Transactions onGraphics (Proceedings of SIGGRAPH Asia) 31, 6 (Nov. 2012), 192:1–192:10. https:
```

//doi.org/10/gbb6q7Iliyan Georgiev, Zackary Misso, Toshiya Hachisuka, Derek Nowrouzezahrai, Jaroslav

```
Křivánek, and Wojciech Jarosz. 2019. Integral Formulations of Volumetric Transmit-tance. ACM Transactions on Graphics (Proceedings of SIGGRAPH Asia) 38, 6 (Nov.
```

```
2019), 154:1–154:17. https://doi.org/10/dffnMichael B. Giles. 2008. Multilevel Monte Carlo Path Simulation. Operations Research
```

```
56, 3 (June 2008), 607–617. https://doi.org/10/fmrpfpToshiya Hachisuka, Wojciech Jarosz, and Henrik Wann Jensen. 2010. A Progressive
```

```
Error Estimation Framework for Photon Density Estimation. ACM Transactions onGraphics (Proceedings of SIGGRAPH Asia) 29, 6 (Dec. 2010), 144:1–144:12. https:
```

//doi.org/10/dmttfg

```
Toshiya Hachisuka and Henrik Wann Jensen. 2009. Stochastic Progressive PhotonMapping. ACM Transactions on Graphics (Proceedings of SIGGRAPH Asia) 28, 5 (Dec.
```

```
2009), 130:1–130:8. https://doi.org/10/d8xxn3S. Heinrich. 1998. A Multilevel Version of the Method of Dependent Tests. In Proc. of the
```

3rd St. Petersburg Workshop on Simulation. St. Petersburg University Press, 31–35.Adrian Jarabo, Carlos Aliaga, and Diego Gutierrez. 2018. A Radiative Transfer Frame-

```
work for Spatially-Correlated Materials. ACM Transactions on Graphics (Proceedingsof SIGGRAPH) 37, 4 (July 2018), 83:1–83:13. https://doi.org/10/gd52qq
```

Wojciech Jarosz, Derek Nowrouzezahrai, Iman Sadeghi, and Henrik Wann Jensen.2011a. A Comprehensive Theory of Volumetric Radiance Estimation Using Photon

```
Points and Beams. ACM Transactions on Graphics 30, 1 (Jan. 2011), 5:1–5:19. https://doi.org/10/fcdh2f
```

```
Wojciech Jarosz, Derek Nowrouzezahrai, Robert Thomas, Peter-Pike Sloan, and MatthiasZwicker. 2011b. Progressive Photon Beams. ACM Transactions on Graphics (Proceed-
```

```
ings of SIGGRAPH Asia) 30, 6 (Dec. 2011), 181:1–181:12. https://doi.org/10/fn5xzjHenrik Wann Jensen. 2001. Realistic Image Synthesis Using Photon Mapping. AK Peters,
```

Ltd., Natick, MA, USA.Jiantao Jiao and Yanjun Han. 2020. Bias Correction with Jackknife, Bootstrap, and

```
Taylor Series. IEEE Transactions on Information Theory 66, 7 (July 2020), 4392–4418.https://doi.org/10/gj32t9
```

Daniel Jonsson, Joel Kronander, Jonas Unger, Thomas B. Schon, and Magnus Wrenninge.2020. Direct Transmittance Estimation in Heterogeneous Participating Media Using

```
Approximated Taylor Expansions. IEEE Transactions on Visualization and ComputerGraphics (2020), 1–1. https://doi.org/10/gj32rc
```

A. Keller. 2001. Hierarchical Monte Carlo Image Synthesis. Mathematics and Computersin Simulation 55, 1-3 (2001), 79–92.

```
Markus Kettunen, Eugene d’Eon, Jacopo Pantaleoni, and Jan Novak. 2021. An UnbiasedRay-Marching Transmittance Estimator. (Feb. 2021). arXiv:2102.10294 [cs.GR]
```

```
Claude Knaus and Matthias Zwicker. 2011. Progressive Photon Mapping: A ProbabilisticApproach. ACM Transactions on Graphics 30, 3 (May 2011), 25:1–25:13. https:
```

//doi.org/10/bcw2phPeter Kutz, Ralf Habel, Yining Karl Li, and Jan Novák. 2017. Spectral and Decomposition

```
Tracking for Rendering Heterogeneous Volumes. ACM Transactions on Graphics(Proceedings of SIGGRAPH) 36, 4 (July 2017), 111:1–111:16. https://doi.org/10/gbxjxg
```

```
Don McLeish. 2011. A General Method for Debiasing a Monte Carlo Estimator. MonteCarlo Methods and Applications 17, 4 (Jan. 2011). https://doi.org/10/c2fpdx
```

Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz. 2022. Unbiasedand consistent rendering using biased estimators supplemental code and data. https:
//doi.org/10.5281/zenodo.6515009Sarat Babu Moka, Dirk P. Kroese, and Sandeep Juneja. 2019. Unbiased Estimation of the

```
Reciprocal Mean for Non-Negative Random Variables. In 2019 Winter SimulationConference (WSC). 404–415. https://doi.org/10/ggr944
```

Jan Novák, Andrew Selle, and Wojciech Jarosz. 2014. Residual Ratio Tracking forEstimating Attenuation in Participating Media. ACM Transactions on Graphics

```
(Proceedings of SIGGRAPH Asia) 33, 6 (Nov. 2014), 179:1–179:11. https://doi.org/10/f6r2nq
```

Adithya Pediredla, Yasin Karimi Chalmiani, Matteo Giuseppe Scopelliti, MaysamrezaChamanzar, Srinivasa Narasimhan, and Ioannis Gkioulekas. 2020. Path Tracing Esti-

```
mators for Refractive Radiative Transfer. ACM Transactions on Graphics (Proceedingsof SIGGRAPH Asia) 39, 6 (Nov. 2020), 241:1–241:15. https://doi.org/10/gj4msh
```

```
Matt Pharr, Wenzel Jakob, and Greg Humphreys. 2016. Physically Based Rendering:From Theory to Implementation (3rd ed.). Morgan Kaufmann, Cambridge, MA.
```

```
Hao Qin, Xin Sun, Qiming Hou, Baining Guo, and Kun Zhou. 2015. Unbiased PhotonGathering for Light Transport Simulation. ACM Transactions on Graphics 34, 6 (Oct.
```

```
2015). https://doi.org/10/f7wrc6Chang-han Rhee. 2013. Unbiased Estimation with Biased Samplers. Ph. D. Dissertation.
```

Stanford University.Chang-han Rhee and Peter W. Glynn. 2012. A New Approach to Unbiased Estimation

```
for SDE’s. (July 2012). arXiv:1207.2452 [q-fin.CP]Chang-Han Rhee and Peter W. Glynn. 2015. Unbiased Estimation with Square Root
```

```
Convergence for SDE Models. Operations Research 63, 5 (Oct. 2015), 1026–1043.https://doi.org/10/f7xf6m
```

Delio Vicini, Wenzel Jakob, and Anton Kaplanyan. 2021. A Non-Exponential Transmit-tance Model for Volumetric Scene Representations. ACM Transactions on Graphics

```
(Proceedings of SIGGRAPH) 40, 4 (Aug. 2021), 136:1–136:16. https://doi.org/10/hshgJiří Vorba and Jaroslav Křivánek. 2016. Adjoint-Driven Russian Roulette and Split-
```

```
ting in Light Transport Simulation. ACM Transactions on Graphics (Proceedings ofSIGGRAPH) 35, 4 (July 2016), 42:1–42:11. https://doi.org/10/f89mcz
```

```
Christopher S. Withers. 1987. Bias Reduction by Taylor Series. Communications inStatistics - Theory and Methods 16, 8 (Jan. 1987), 2369–2383. https://doi.org/10/
```

bmqbg4Tizian Zeltner, Iliyan Georgiev, and Wenzel Jakob. 2020. Specular Manifold Sampling

```
for Rendering High-Frequency Caustics and Glints. ACM Transactions on Graphics(Proceedings of SIGGRAPH) 39, 4 (July 2020). https://doi.org/10/gg8xc8
```

ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
48:12 • Zackary Misso, Benedikt Bitterli, Iliyan Georgiev, and Wojciech Jarosz
A VARIANCE-OPTIMAL SINGLE-TERM ESTIMATION

```
Here we derive the variance-optimal PDF/PMF 𝑝 (𝑥) for the integral
```

```
estimator in Eq. (14) in the continuous and discrete case.
```

Continuous case. Since the estimator is unbiased, minimizing its
variance is equivalent to minimizing its second moment,
E

```
[(
```

⟨Δ𝑗 ⟩

```
𝑝 ( 𝑗)
```

```
)2]
```

=
∫ ∞
𝑘
E[⟨Δ𝑥 ⟩2]

```
𝑝 (𝑥)2 𝑝 (𝑥) d𝑥 =
```

∫ ∞
𝑘
E[⟨Δ𝑥 ⟩2]

```
𝑝 (𝑥) d𝑥, (28)
```

```
under the condition that 𝑝 (𝑥) is normalized, i.e., ∫ ∞𝑘 𝑝 (𝑥) d𝑥 = 1.
```

This problem can be solved using the Euler-Lagrange equation from
the calculus of variations as follows. We first define

```
L(𝑥, 𝜆, 𝑝) = E
```

[⟨Δ
𝑥 ⟩2
]

```
𝑝 (𝑥) + 𝜆𝑝 (𝑥), (29)
```

```
where 𝜆 is the (yet unknown) Lagrange multiplier. We then write
```

the Euler-Lagrange equation for 𝑞, which we solve for 𝑝:
dL
d𝑝 −
d
d𝑥

```
( dL
```

d𝑝 ′

```
)
```

=0
= 0 ⇔ − E
[⟨Δ
𝑥 ⟩2
]

```
𝑝2 (𝑥) + 𝜆 = 0 (30)
```

```
⇔ 𝑝 (𝑥) =
```

√
E[⟨Δ𝑥 ⟩2]

```
𝜆 . (31)
```

```
Since 𝑝 (𝑥) must be normalized, 𝜆 is its normalization constant.
```

```
Finally, since V[⟨Δ𝑥 ⟩] = E[⟨Δ𝑥 ⟩2] − (Δ𝑥 )2, we minimize vari-
```

ance when

```
𝑝 (𝑥) ∝
```

√

```
V[⟨Δ𝑥 ⟩] + (Δ𝑥 )2. (32)
```

Discrete case. In this case the second moment takes the form
E

```
[(
```

⟨Δ𝑗 ⟩

```
𝑝 ( 𝑗)
```

```
)2]
```

=
∞Õ
𝑗=𝑘
E[⟨Δ𝑗 ⟩2]

```
𝑝 ( 𝑗) . (33)
```

```
To find the minimum of this sum w.r.t. 𝑝 ( 𝑗), we use the method of
```

Lagrange multipliers. We define a new minimization problem

```
L (𝜆, 𝑝) =
```

∞Õ
𝑗=𝑘
E[⟨Δ𝑗 ⟩2]

```
𝑝 ( 𝑗) − 𝜆
```

©
«
1 −
∞Õ
𝑗=𝑘

```
𝑝 ( 𝑗)ª®
```

¬

```
(34)
```

and find its local extrema by solving for roots of its gradient. The
sum in the parentheses encodes the PMF normalization condition.

```
Solving for 𝑝 ( 𝑗) yields
```

𝜕L

```
𝜕𝑝 ( 𝑗) = 0 ⇔ −
```

E[⟨Δ𝑗 ⟩2]

```
𝑝 ( 𝑗)2 + 𝜆 = 0 (35)
```

```
⇔ 𝑝 ( 𝑗) =
```

√
E[⟨Δ𝑗 ⟩2]

```
𝜆 ⇔ 𝑝 ( 𝑗) ∝
```

√

```
V[⟨Δ𝑗 ⟩] + (Δ𝑗)2, (36)
```

```
where in Eq. (36) 𝜆 is a normalization constant, arriving at an optimal
```

PMF analogous to the one for the continuous case above.
B CONDITIONS FOR CONSISTENCY
For a secondary estimator to be consistent, we need its MSE to

```
converge:
```

lim𝑁 →∞ MSE[⟨𝐼 ⟩𝑁 ] = lim𝑁 →∞

```
(
```

V[⟨𝐼 ⟩𝑁 ] + B[⟨𝐼 ⟩𝑁 ]2

```
)
```

```
= 0. (37)
```

For this we need both the bias and the variance to converge:
lim𝑁 →∞ V[⟨𝐼 ⟩𝑁 ] = lim𝑁 →∞1𝑁 2
𝑁Õ
𝑖=1

```
V[⟨𝐼 (𝑘𝑖 )⟩]
```

```
𝑉 (𝑘𝑖 )
```

```
= O(𝑉 (𝑘𝑁 ))𝑁 = 0, (38)
```

lim𝑁 →∞ B[⟨𝐼 ⟩𝑁 ] = lim𝑁 →∞1𝑁
𝑁Õ
𝑖=1

```
B[⟨𝐼 (𝑘𝑖 )⟩]
```

```
𝐵 (𝑘𝑁 )
```

```
= O(𝐵(𝑘𝑁 )) = 0, (39)
```

This result tells us that consistency is achieved when the primary

```
estimator’s bias 𝐵(𝑘) vanishes, at any rate, while its variance is even
```

allowed to increase, though sublinearly. Among all parameteriza-
tions for 𝑘𝑁 that meet these two conditions, the one that maximizes

```
the MSE convergence rate is the one that achieves O(V[⟨𝐼 ⟩𝑁 ]) =
```

O

```
(
```

B[⟨𝐼 ⟩𝑁 ]2

```
)
```

```
, i.e. O(𝑉 (𝑘𝑁 )) = 𝑁 O (𝐵2 (𝑘𝑁 )).
```

C DEBIASING PHOTON MAPPING
In the following we describe the steps to debias photon mapping.

```
We begin with the biased but consistent base estimator ⟨𝐼 (𝑘)⟩ which
```

traces 𝑀𝑘 photons and performs density estimation with a kernel of
radius 𝑟𝑘 . For suitably chosen 𝑀𝑘 and 𝑟𝑘 , this estimator converges
to 𝐼 as 𝑘 → ∞ [Jensen 2001].

```
We form a single-term telescoping-series estimator (14) assuming
```

```
perfectly correlated evaluation of ⟨Δ𝑗 ⟩ = ⟨𝐼 ( 𝑗 + 1)⟩ − ⟨𝐼 ( 𝑗)⟩, i.e. both
```

```
evaluations of ⟨𝐼 ( 𝑗)⟩ and ⟨𝐼 ( 𝑗 + 1)⟩ share the same set of photons. If
```

```
both estimators trace different numbers of photons (i.e. 𝑀𝑗+1 ≠ 𝑀𝑗 ),
```

we ignore unshared photons for the rest of this analysis, giving a
lower bound on the variance and bias. Under this assumption, evalu-

```
ation of the two estimators differs only in the kernel radius used (𝑟 𝑗
```

```
and 𝑟 𝑗+1), and we can express the difference of the two estimators
```

as a single photon mapping estimator that uses the difference of the
two kernels for density estimation.
This allows us to use the analysis of Knaus and Zwicker [2011]
as a basis to derive the expectation and variance of ⟨Δ𝑗 ⟩ which
are needed for deriving a variance-optimal PMF for sampling the
telescoping series. Repeating the derivation of Knaus and Zwicker
using the modified difference kernel yields the following asymptotic

```
relationships:
```

V[⟨Δ𝑗 ⟩] ∝ 1𝑀𝑗

```
∫ (
```

```
𝑘 (𝑟 𝑗+1, 𝑥) − 𝑘 (𝑟 𝑗 , 𝑥))2 d𝑥, (40)
```

```
Δ𝑗 ∝ 𝑟 2𝑗 , (41)
```

```
where 𝑘 (𝑟, 𝑥) evaluates the density-estimation kernel of radius 𝑟 at
```

location 𝑥.
The asymptotics above depend on the relationship of the number
of photons 𝑀𝑘 and the kernel radius 𝑟𝑘 with respect to 𝑘, as well as
the specific choice of kernel. Knaus and Zwicker [2011] and Georgiev
et al . [2012] show that 𝑟 𝑗 =
√
𝑗𝛼−1 with 0 < 𝛼 < 1 yields consistent
progressive estimation. This leads to the following asymptotics for
the expectation and the variance:

```
Δ𝑗 = O( 𝑗𝛼−2) (42)
```

```
V[⟨Δ𝑗 ⟩] = 𝑀−1𝑗 O( 𝑗−𝛼 ), (constant kernel) (43)
```

```
V[⟨Δ𝑗 ⟩] = 𝑀−1𝑗 O( 𝑗−𝛼−1). (cone kernel) (44)
```

ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
Unbiased and consistent rendering using biased estimators • 48:13
Given the asymptotics, we can now test whether debiasing yields
finite work-normalized variance. First, the optimal PMF

```
𝑝 ( 𝑗) ∝
```

√

```
V[⟨Δ𝑗 ⟩] + (Δ𝑗)2 =
```

√

```
𝑀−1𝑗 O( 𝑗−𝛼−1) + O( 𝑗2𝛼−4) (45)
```

```
must be normalizable (using the best-case, cone-kernel variance).
```

Second, the expected work
C[⟨𝐼 ⟩1] ∝
∞Õ
𝑗=1

```
𝑀𝑗 · 𝑝 ( 𝑗) ∝
```

∞Õ
𝑗=1
√

```
𝑀𝑗 O( 𝑗−𝛼−1) + 𝑀2𝑗 O( 𝑗2𝛼−4) (46)
```

```
must be finite (here, using the number of emitted photons as an
```

```
estimate of the cost). Sadly, there is no choice of 𝑀𝑗 and 𝛼 that can
```

satisfy both these conditions. The estimator is still debiasable, but
with infinite work-normalized variance, i.e., with reduced secondary-
estimator convergence rate.
D IDEAL-CASE FINITE-DIFFERENCE ANALYSIS
D.1 Expectation & variance of finite-difference deltas

```
To form an estimator of ΔFD𝑗 (21), we first need to estimate the
```

```
integrals in Eq. (20). In the ideal case, we can perfectly correlate
```

```
evaluations of 𝑓 (𝑥, 𝑦) through the use of the same samples for 𝑦,
```

```
so for brevity we will simplify 𝑓 (𝑥, 𝑦) to 𝑓 (𝑥) in the following
```

derivations. This results in

```
⟨ΔFD𝑗 ⟩ = ⟨𝑓 (𝑥 + ℎ𝑗+1)⟩ − ⟨𝑓 (𝑥)⟩ℎ𝑗+1− ⟨𝑓 (𝑥 + ℎ𝑗 )⟩ − ⟨𝑓 (𝑥)⟩ℎ𝑗. (47)
```

```
If 𝑓 (𝑥) is continuously differentiable with respect to 𝑥, we have
```

```
𝑓 (𝑥 + ℎ) = 𝑓 (𝑥) + ℎ 𝜕𝜕𝑥 𝑓 (𝑥) + ℎ2 𝜕
```

2

```
𝜕𝑥2 𝑓 (𝑥) + O(ℎ
```

```
3) . (48)
```

```
Inserting Eq. (48) into (47) and canceling terms gives
```

```
⟨ΔFD𝑗 ⟩ = (ℎ𝑗+1 − ℎ𝑗 )
```

〈 𝜕2

```
𝜕𝑥2 𝑓 (𝑥)
```

〉

- O(ℎ2𝑗+1) − O(ℎ2𝑗 ) , (49)
  and since ℎ𝑗+1 < ℎ𝑗 by construction, we have

```
ΔFD𝑗 ∝ (ℎ𝑗+1 − ℎ𝑗 ), and V[⟨ΔFD𝑗 ⟩] ∝ (ℎ𝑗+1 − ℎ𝑗)2 . (50)
```

D.2 Bias & variance rates of consistent finite differences

```
For the ideal case where all evaluations of 𝑓 (𝑥, 𝑦) can be evaluated
```

```
using the same samples for 𝑦 Eq. (47), estimating 𝐼 (𝑘) in Eq. (20) is
```

equivalent to estimating the true derivative convolved with a box

```
kernel (for brevity, we use 𝑓 (𝑥) since we evaluate each 𝑓 (𝑥, 𝑦) using
```

```
a shared sample 𝑦):
```

```
⟨𝐼 (𝑘)⟩ = ⟨𝑓 (𝑥 + ℎ𝑘 ) − 𝑓 (𝑥)⟩ℎ
```

𝑘
= 1ℎ
𝑘
∫ 𝑥+ℎ𝑘
𝑥
〈 𝜕

```
𝜕𝑥 𝑓 (𝑡)
```

```
〉 d𝑡 (51)
```

=
∫ ∞

```
−∞𝐾 (𝑥 − 𝑡)
```

〈 𝜕

```
𝜕𝑥 𝑓 (𝑡)
```

```
〉 d𝑡, where (52)
```

```
𝐾 (𝜏) =
```

```
{ 1
```

ℎ𝑘 0 < 𝜏 < ℎ𝑘

```
0 otherwise is a normalized box kernel. (53)
```

```
If we replace 〈 𝜕𝜕𝑥 𝑓 (𝑡)〉 with its expectation, this shows that the
```

```
bias in finite difference estimators results from a 1D blur (along the
```

```
direction of differentiation), analogously to how photon beams [Jarosz
```

et al. 2011a] return a 1D blurred version of volumetric radiance.

```
Given this equivalence, a direct Monte Carlo estimator of Eq. (20)
```

will have the same bias and variance convergence rates as derived by
Jarosz et al. [2011b] for photon beams when the parameter of differ-
entiation does not modify the path space, with the finite difference
step size ℎ𝑘 standing in for the blur kernel width:

```
B[⟨𝐼 (𝑘)⟩] = O(ℎ𝑘 ) and V[⟨𝐼 (𝑘)⟩] = O
```

```
(
```

ℎ−1𝑘

```
)
```

```
. (54)
```

This implies that, just like in progressive photon mapping, we can
form a progressive finite difference estimator by averaging multiple
finite difference renderings while reducing the step size ℎ𝑘 according
to ℎ𝑘 = ℎ0
√
𝑘𝑎−1. This is guaranteed to be a consistent estimator

```
for parameter 𝑎 ∈ (0, 1), and provides its optimal MSE convergence
```

rate with 𝑎 = 2/3.
More generally, by the law of large numbers progressive estima-
tors will still converge even if all 𝑦 samples cannot be correlated,
however, the convergence rate will be slower then our derived ideal

```
rates Eq. (54).
```

E DERIVING CONSISTENT PROGRESSIVE ESTIMATION
FROM UNBIASED ESTIMATION
We first construct an unbiased progressive secondary estimator

```
Eq. (16) with 𝑘𝑖 = 𝑖, and replace the primary estimator with its
```

```
expectation:
```

𝐼 = 1𝑁
𝑁Õ
𝑘=0
©
«

```
𝐼 (𝑘) +
```

∞Õ
𝑗=𝑘
Δ𝑗 ª®
¬

```
(55)
```

= 1𝑁
𝑁Õ
𝑘=0

```
𝐼 (𝑘) +
```

𝑁Õ
𝑘=0
∞Õ
𝑗=𝑘
Δ𝑗

```
𝑁 . (56)
```

From here it is easy to see that since all Δ𝑗 ’s are finite by construction

```
(Δ∞ = 0), the right (i.e. bias) term in Eq. (56) converges to zero:
```

lim𝑁 →∞
𝑁Õ
𝑘=0
∞Õ
𝑗=𝑘
Δ𝑗
𝑁 = lim𝑁 →∞
1
𝑁
𝑁Õ
𝑘=0
∞Õ
𝑗=𝑘
Δ𝑗 = lim𝑁 →∞1𝑁
𝑁Õ
𝑘=0

```
𝑎𝑘 = 0. (57)
```

Choosing to never evaluate the bias yields a biased but consistent
progressive formulation:
𝐼 = lim𝑁 →∞1𝑁
𝑁Õ
𝑘=0

```
𝐼 (𝑘). (58)
```

ACM Trans. Graph., Vol. 41, No. 4, Article 48. Publication date: July 2022.
