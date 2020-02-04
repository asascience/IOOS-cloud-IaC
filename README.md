# IOOS-cloud-IaC

### Directory structure

    .
    ├── CFNTemplates        # AWS CloudFormation templates
    ├── Docker              # Dockerfiles
    ├── python              # Python3 modules
    │   ├── cluster         # Cluster abstract base class and implementations 
    │   ├── configs         # cluster configuration files (JSON)
    │   ├── job             # Job abstract base class and implementations
    │   ├── jobs            # job configuration files (JSON)
    │   ├── plotting        # plotting and mp4 routines
    │   ├── services        # Cloud agnostic interfaces and implementations e.g. S3
    │   ├── 
    │   └── workflows       # Workflows and workflow tasks
    ├── romsUtil.py         # Various utility functions, e.g. 
    └── README.md
