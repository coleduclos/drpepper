# Overview
Below is the proposed design for Dr Pepper's migration to the cloud. This document is broken into three sections: 

1. Current architecture and requirements for the migration. 
2. Technologies to be used in the cloud and the architecture design. 
3. Suggestions for redesign of the application post migration.

---

# Section 1
## Current Architecture
| Technology | Purpose |
| ---------- | ------- |
| PHP | Web Application |
| SQLite | Database |
| Riak | Database |

## Requirements
| Requirement | Description | 
| ----------- | ----------- |
| Internet Facing | Web app is internet facing for customers to access. |
| High Reliability | Current architecture on Toshiba tablets is causing reliability issues. |
| High Security | Hackers are trying to access Dr Pepper's secret sauce. If this were to happen, business would collapse. Must protect WebApp and DBs |

## Assumptions
| Assumption | Impact |
| ---------- | ------ | 
| SQLite is read-only | Can be stored in highly available central location, without having to worry about write locks when clustering application | 

---

# Section 2
## Technologies to be Used
### Amazon Web Services (AWS)

AWS is a public cloud computing platform consisting of many remote ondemand services addressing customers' needs in compute, stroage, databases, networking, and security. AWS enables sophisticated applications by increasing flexibility, scalability, and reliability. 

#### Accounts & Governance
| Type          | Description |
| ------------- | ----------- |
| AWS Account | Overall account that houses all AWS resources (created once). |
| IAM Account | Individual logins / user granted access to AWS Account. |
| IAM Role    | AWS "hat" that a user or resource can wear allowing certain actions to be performed (permissions attached) |
| IAM Policy  | Document that explicitly lists permissions. Can be attached to user, group, role, or resouce. |


#### Reliability
AWS operates in many regions around the world. Each region is made up of multiple isolated availability zones (AZs). By deploying accross multiple regions and AZs, an application can avoid failures and increase resiliancy. 

| Region Code | Region Name |
| ----------- | ----------- | 
| us-east-1 | US East (N. Virginia) | 
| us-west-2 | US West (Oregon) | 
| us-west-1 | US West (N. California) |
| eu-west-1 | EU (Ireland) | 
| eu-central-1 | EU (Frankfurt) | 
| ap-southeast-1 | Asia Pacific (Singapore) | 
| ap-northeast-1 | Asia Pacific (Tokyo) | 
| ap-southeast-2 | Asia Pacific (Sydney) | 
| ap-northeast-2 | Asia Pacific (Seoul) | 
| ap-south-1 | Asia Pacific (Mumbai) | 
| sa-east-1 | South America (São Paulo) | 
**Note:** Availability Zones are represented by a region code followed by a letter identifier (eg. us-east-1a). 

#### Networking
| Service / Component | Description |
| ------------------- | ----------- |
| VPC | Virtual Private Cloud - logically isolated network dedicated to an AWS account that you define. This secure virtual network is where you launch AWS resources and can control inbound / outbound traffic. |
| public subnet  | Block of VPC IP addresses assigned to one AZ meant for internet facing resources such as customer facing webservers. |
| private subnet | Block of VPC IP addresses assigned to one AZ meant for resources that **do not** need direct internet access such as databases. |
| ELB | Elastic Load Balancer - Automatically routes traffic across multiple healthy instances and AZs while automatically scaling its request handling capacity to meet demands. |
| Route 53 | Highly available and scalable Domain Name System (DNS) that connects user requests to ELBs |
| Internet Gateway | Highly available component that allows communication between instances in VPC and the internet. | 
| Route Table | Each VPC has an implicit router. The routetable contains the set of rules used to determine where network traffic is directed. | 
| Security Group | Virtual firewall that controls inbound / outbound trafic to instances. |  
| NAT Instance | Network Address Translation Instance - used in a public subnet to enable **outbound** internet traffic from instances on private subnet but prevent inbound traffic to that instance. |


#### Compute
| Service / Component | Description |
| ------------------- | ----------- |
| EC2 | Elastic Compute Cloud - easily configurable, scalable, and resizable compute capacity in the cloud. |
| AMI | Amazon Machine Image - base information required to launch an EC2 instance (including the OS, prebaked software, permissions, etc.). |

#### Storage & Database
| Service / Component | Description |
| ------------------- | ----------- |
| S3 | Simple Storage Service - secure and highly-scalable object storage with simple web interface to store / retrieve. |
| EFS | Elastic File Storage - file storage with automatic capacity adjusment (elastic) and simple interface to create / configure file systems. | 
| RDS | Relational Database Service - provides inexpensive, easy, scalable, fast, secure, and highly avaialble relational databases in the cloud. |

#### Logging & Monitoring
| Service / Component | Description | 
| ------------------- | ----------- |
| CloudWatch | Collects and tracks metrics / log files, sets alarms, and enables automatically reaction to changes in your AWS resources. |
| CloudTrail | Records AWS API calls for your account (includes identity of caller, time, source, response, etc.) | 

#### Scalability
| Service / Component | Description | 
| ------------------- | ----------- |
| ASG	| Auto Scaling Group - maintain application availability and/or scale compute capacity according to demand (conditions you define - measured using CloudWatch). | 
| Launch Config | Template for ASG to launch EC2 instances (includes AMI, instance type, security group, etc.) | 

### F5 WAF
F5 is a Web Application Firewall (WAF) designed to protect webservers from malicious attacks such as:
* Cross-site scripting
* SQL Injection
* Forceful browsing
* Cookie poisoning
* Invaid Input

## Proposed Architecture Design
Below is a diagram of the proposed Dr Pepper architecture in AWS:

![alt text](https://github.com/coleduclos/drpepper/blob/master/Task_1/images/Dr_Pepper_Arch.png "Proposed Dr Pepper Arch")

### Regions
Dr Pepper will utilize both the **us-east-1** and **us-west-2** region to increase availability.

| Region Code | Region Name |
| ----------- | ----------- | 
| us-east-1 | US East (N. Virginia) | 
| us-west-2 | US West (Oregon) |

**Note:** If additional regions are needed in the future, the proposed architecture would remain the same in that region(s).

### Network Design
The VPC will be architected in such a way that enables customers to access the PHP application from the internet, while protecting the application itself and Dr Pepper's data from hackers. 

#### VPC / Subnets
* 1 VPC in each region
* 2 AZs in each VPC for increased availability
* 3 Subnets in each AZ:
  * **public subnet** dedicated to:
    * WAF (F5)
    * NAT Instance
  * **private subnet** dedicated to the web app instances (managed by an ASG)
  * **private subnet** dedicated to Riak database instances

**Route 53** will connect user requests to the ELBs in the public subnet via internet gateways. 

#### Security
**NAT Instance**

AWS has specific NAT AMIs that will be deployed in each of the public subnets allowing egress traffic from the private subnets to the internet and prevent ingress traffic from the internet, ensuring the safety of Dr Pepper's systems.  

**WAF**

F5 WAF will be deployed and scaled automatically based on traffic (the scaling will be similar to the Dr Pepper's web app) in each of the public subnets. These WAFs will protect and block malicious attempts to compromise Dr Pepper's systems. 

### Application Auto Scaling
In AWS, the Dr Pepper application will be automatically scaled up and down based upon the customers' demands using an Auto Scaling Group. To do so, an AMI with the PHP application installed must be created and referenced in the ASG's launch config. AWS will use CloudWatch to monitor the instances and determine when scaling is needed, automatically attaching the new instances to an ELB.  
#### AMI
**PHP application** installed ontop of same base OS that is currently being used.

#### Launch Config
| Property | Configuration |
| -------- | ------------- |
| AMI | Use the same AMI as mentioned above |
| Securtiy Group | Depends on ingress and engress ports needed |
| Instance Type | Depends on the size of the application |

#### ELB
| Property | Configuration |
| -------- | ------------- |
| Subnets | app-private-a, app-private-b |
| Cross Zone | True |
| Listeners | LoadBalancerPort 443 -> InstancePort 443 (HTTPS)|
| HealthCheck | Target = HTTPS:443/, HealthyThreshold = 3, UnhealthyThreshold = 5, Interval = 30, Timeout = 5 |

#### ASG
| Property | Configuration |
| -------- | ------------- |
| Launch Config | Use the same Launch Config as mentioned above |
| SubnetIds | app-private-a app-private-b |
| Min Size | 5 (depends on current load patterns) |
| Max Size | 15 (depends on current load patterns) |
| Load Balancer | ELB mentioned above |
| Tags | Name = drpepper-php-app | 

#### Scale Up Policy
| Property | Configuration |
| -------- | ------------- |
| Adjustment Type | Change In Capacity | 
| Metric Aggregation Type | Average | 
| Policy Type | Step Scaling | 
| Step Adjustment 1 | 1. Metric Interval Lower Bound = 0, Metric Interval Upper Bound = 30, Scaling Adjustment = 1 |
|Step Adjustment 2 | 2. Metric Interval Lower Bound = 30, Metric Interval Upper Bound = Infinity, Scaling Adjustment = 2 | 

#### Scale Down Policy
| Property | Configuration |
| -------- | ------------- |
| Adjustment Type | Change In Capacity | 
| Metric Aggregation Type | Average | 
| Policy Type | Step Scaling | 
| Step Adjustment | 1. Metric Interval Lower Bound = 0, Metric Interval Upper Bound = Infinity, Scaling Adjustment = -1 | 


#### CloudWatch
**High CPU Alarm**

| Property | Configuration |
| -------- | ------------- |
| Evaluation Periods | 1 |
| Statistic | Average |
| Threshhold | 40 |
| Period | 300 |
| Alarm Actions | Scale **Up** Policy mentioned above |
| Namespace | AWS/EC2 |
| Dimensions | AutoScalingGroupName = name of ASG mentioned above |
| Comparison Operator | GreaterThanThreshhold |
| MetricName | CPUUtilization |
	
**Low CPU Alarm**

| Property | Configuration |
| -------- | ------------- |
| Evaluation Periods | 1 |
| Statistic | Average |
| Threshhold | 40 |
| Period | 300 |
| Alarm Actions | Scale **Down** Policy mentioned above |
| Namespace | AWS/EC2 |
| Dimensions | AutoScalingGroupName = name of ASG mentioned above |
| Comparison Operator | LessThanThreshhold |
| MetricName | CPUUtilization |

**Note:** These scaling components can be managed via CloudFormation

### Database
#### SQLite
Since the assumption was made that the SQLite DB is read-only, it will be stored in an S3 Bucket so it can be accessed by all PHP servers without having to worry about backing up, making highly available, etc.

#### Riak
At least 2 EC2 instances of Riak running in each DB dedicated private subnet. 
#### Data Backup
Everyday do an EBS snapshot of all Riak nodes running (one at a time).  

### Logging & Monitoring
The following logs will be stored in **S3 Bucket(s)**:
* AWS CloudTrail
* CloudWatch
* AWS ELB Logs
* EC2 System Logs
* VPC Flow Logs

### IAM Roles
The following AMI roles and attached policies will be created to help govern the AWS Account.

| Role / Policy  | Scope |
| -------- | ------------- |
| Admin | Access all services (manage IAM)  |
| Developer | Access basic compute & storage services: EC2, S3, CloudWatch, CloudFormation, etc. |
| Network Admin | Access and manage networking services |

---

# Section 3
## Post Migration Suggestions
Simplify the application and infrastructure to enable to use of **AWS Elastic Beanstalk**. By doing so, AWS will automatically handle the deployment, auto-scaling, load balancing, and monitoring of Dr Pepper's application.

### Application Redesign
Break down the monolithic application into microservices by:

1. "Strangling" the system - all new features should be architected as microservices.
2. Using small pieces at a time, begin to break apart the system and rearchitect as microservices.
3. Run these microservices in Docker containers, managed by AWS EC2 Container Service or Kubernetes.

### Database
#### Riak
Migrate the Riak DBs to Amazon's DynamoDB Service. DynamoDB is fully managed, integrates with AWS Lambda (enabling apps to automatically change due to data changes), can be backed up with S3, and supports both document and key-value data structures.

#### SQLite 
If the SQLite DB is **not** read only, it is suggested that the DB be migrated to a RDS like AWS Aurora, MySQL, or MariaDB to ensure data consistancy, avoidance of write locks on the DB, etc. 

### Logging & Monitoring
Use AWS Elasticsearch Service to monitor apps in realtime and run log and clickstream analytics. Will require IAM role setup to monitor log data in S3 Bucket. 