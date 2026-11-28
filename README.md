# DDMT

DDMT is a delta debugging approach driven by Metamorphic Testing. It integrates the ddmin algorithm with metamorphic testing, and it can be applied without using test oracles.

---

Here is the artifact for the paper “*Delta Debugging in the Absence of Test Oracles
Through Metamorphic Testing*”.

This artifact contains:

> Implementation of DDMT with five delta debugging variants
> > **ddmin-DDMT**
> > **Perses-DDMT**
> > **ProbDD-DDMT**
> > **WDD-DDMT**
> > **DDImage-DDMT**
> Experiment Replication Package.

> Experimental results.

---
# Implementation details
```
DDMT/
├── Perse-DDMT              # implementation of the integration of Perse and MT
├── ddmin-DDMT/             # implementation of the integration of ddmin and MT
│   ├── src/                # implementaion of auxiliary functions and MRs for subject programs
│   ├── printtokens/        # scripts for runing ddmin-DDMT
│   ├── replace/            # scripts for runing ddmin-DDMT
│   └── schedule/           # scripts for runing ddmin-DDMT
├── DDImage-DDMT/             # implementation of the integration of DDImage and MT
│   ├── src/                # implementaion of DDImage_DDMT and MRs for image classification
│   ├── run                # steps for running DDImage_DDMT
├── benchmarks/             # Experimental results
│   ├── Compilers/          # results and subjects of C compilers
│   ├── Siemens/            # summary of results on Siemens programs
│   ├── Siemens/            # summary of results on Image classifiers

```
---

The experimental operating environment are described as below.

```
   Ubuntu 16.04

   Python 3.0
```
