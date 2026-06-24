# DDMT

DDMT is a delta debugging approach driven by Metamorphic Testing. It integrates the ddmin algorithm with metamorphic testing, and it can be applied without using test oracles.

---

Here is the artifact for the paper “*Delta Debugging in the Absence of Test Oracles
Through Metamorphic Testing*”.

This artifact contains:

> Implementation of DDMT with two delta debugging variants, Perses-DDMT and ddmin-ddmt.

> Experiment Replication Package.

> Experimental results.

---
# Implementation details
DDMT/
├── Perse-DDMT              # implementation of the integration of Perse and MT
├── ddmin-DDMT/             # implementation of the integration of ddmin and MT
│   ├── src/                # implementaion of auxiliary functions and MRs for subject programs
│   ├── printtokens/        # scripts for runing ddmin-DDMT
│   ├── replace/            # scripts for runing ddmin-DDMT
│   └── schedule/           # scripts for runing ddmin-DDMT
├── benchmarks/             # Test applications
│   ├── Compilers/          # results and subjects of C compilers
│   ├── Siemens/            # summary of results on Siemens programs

---

The experimental operating environment are described as below.

```
   Ubuntu 16.04

   Python 3.0
```
