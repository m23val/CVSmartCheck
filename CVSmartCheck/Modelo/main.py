from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import fitz
from docx import Document
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
from pathlib import Path
import re
import random
from typing import List, Dict, Tuple, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# === Configuración ===
RUTA_CV_IDEAL = "base_model/cv_ideal.docx"
MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === Clase generadora de recomendaciones ===
class CVRecommendationGenerator:
    """
    Generador de recomendaciones para CVs basado en reglas y análisis de texto
    sin necesidad de APIs externas.
    """
    
    def __init__(self):
        # Palabras clave por puesto
        self.conocimiento_puesto = {
            "Desarrollador Full Stack": {
                "tecnologías_clave": ["full stack", "React", "Next.js", "TypeScript", "Node.js", "Express", "Python", "Django", "FastAPI", 
                                     "MongoDB", "PostgreSQL", "Redis", "Docker", "Kubernetes", "GraphQL", "REST", "AWS", "Azure", 
                                     "GCP", "CI/CD", "GitHub Actions", "Testing", "Jest", "React Testing Library", "Cypress"],
                "habilidades_técnicas": ["arquitectura de microservicios", "desarrollo web progresivo", "aplicaciones serverless", 
                                        "optimización de rendimiento", "SEO técnico", "desarrollo dirigido por pruebas (TDD)", 
                                        "integración continua", "despliegue continuo", "DevOps", "seguridad web"],
                "habilidades_blandas": ["resolución de problemas complejos", "comunicación técnica", "gestión del tiempo", 
                                       "trabajo en equipo ágil", "mentoría", "capacidad de aprendizaje continuo", 
                                       "adaptabilidad tecnológica"],
                "certificaciones_valoradas": ["AWS Developer Associate", "Azure Developer Associate", "MongoDB Developer", 
                                            "Professional Scrum Developer", "Docker Certified Associate", "Kubernetes Developer"],
                "tendencias_2025": ["Web Components", "WebAssembly", "Edge Computing", "Jamstack", "Optimización para Core Web Vitals",
                                   "Zero Trust Security", "API-first design", "Desarrollo Headless", "MACH Architecture"]
            },
            "Ingeniero DevOps": {
                "tecnologías_clave": ["Kubernetes", "Docker", "Terraform", "Ansible", "Jenkins", "GitHub Actions", "CircleCI", 
                                     "ArgoCD", "Prometheus", "Grafana", "ELK Stack", "AWS", "Azure", "GCP", "Linux", "Bash", 
                                     "Python", "Go", "Istio", "Vault", "Linkerd", "GitOps"],
                "habilidades_técnicas": ["infraestructura como código (IaC)", "automatización de procesos", "seguridad DevSecOps", 
                                        "observabilidad", "arquitectura de nube", "escalabilidad", "optimización de costos en la nube", 
                                        "service mesh", "zero-downtime deployments", "gestión de secretos"],
                "habilidades_blandas": ["pensamiento sistémico", "resolución de problemas complejos", "comunicación entre equipos", 
                                       "gestión de incidentes", "mentoría", "documentación técnica", "comunicación de riesgos"],
                "certificaciones_valoradas": ["Certified Kubernetes Administrator (CKA)", "AWS DevOps Engineer Professional", 
                                            "Azure DevOps Engineer Expert", "HashiCorp Terraform Associate", "Red Hat Certified Engineer (RHCE)",
                                            "Site Reliability Engineering (SRE) certification", "GitOps Certification"],
                "tendencias_2025": ["Platform Engineering", "FinOps", "DevSecOps integrado", "Shift-Left Security", 
                                   "Infraestructura Inmutable", "GitOps", "ML-enabled Operations", "Zero Trust Security",
                                   "Internal Developer Platforms", "Cloud Cost Optimization"]
            },
            "Especialista en Ciberseguridad": {
                "tecnologías_clave": ["Pentest", "SIEM", "SOAR", "EDR", "XDR", "Kali Linux", "Metasploit", "Nmap", "Wireshark", 
                                     "OWASP ZAP", "Burp Suite", "Splunk", "QRadar", "Snort", "Falco", "Crowdstrike", "Firebase",
                                     "Zero Trust", "IAM", "HashiCorp Vault", "AWS Security Hub", "Azure Sentinel"],
                "habilidades_técnicas": ["ethical hacking", "análisis forense digital", "análisis de malware", "threat hunting", 
                                        "gestión de vulnerabilidades", "arquitecturas Zero Trust", "seguridad en la nube", 
                                        "seguridad de contenedores", "respuesta a incidentes", "análisis de riesgos"],
                "habilidades_blandas": ["pensamiento analítico", "razonamiento crítico", "comunicación clara de riesgos", 
                                       "trabajo bajo presión", "atención al detalle", "ética profesional", 
                                       "aprendizaje continuo", "colaboración interdepartamental"],
                "certificaciones_valoradas": ["CISSP", "CEH", "OSCP", "GIAC", "CompTIA Security+", "AWS Security Specialty", 
                                            "Certified Cloud Security Professional (CCSP)", "CISM", "CRISC", "eLearnSecurity"],
                "tendencias_2025": ["Seguridad en Entornos Sin Perímetro", "AI/ML para Detección de Amenazas", "Threat Intelligence", 
                                   "Seguridad en Entornos Cuánticos", "Ciberseguridad para Remote Work", "Supply Chain Security",
                                   "API Security", "Seguridad para IoT Industrial", "SASE", "Cloud Security Posture Management"]
            },
            "Ingeniero de Datos": {
                "tecnologías_clave": ["Apache Spark", "Kafka", "Airflow", "dbt", "Snowflake", "Databricks", "AWS Glue", "Delta Lake", 
                                     "Google BigQuery", "Amazon Redshift", "Azure Synapse", "Hadoop", "Hive", "Python", "SQL", "NoSQL", 
                                     "Terraform", "Docker", "Kubernetes", "Iceberg", "Trino"],
                "habilidades_técnicas": ["modelado de datos", "ETL/ELT", "data warehousing", "data lakes", "data lakehouse", 
                                        "streaming data", "batch processing", "data governance", "data quality", "data lineage", 
                                        "data catalogs", "optimización de queries", "distributed computing"],
                "habilidades_blandas": ["pensamiento analítico", "comunicación interdepartamental", "traducción de necesidades de negocio", 
                                       "gestión de expectativas", "documentación", "colaboración con equipos de analítica"],
                "certificaciones_valoradas": ["AWS Data Analytics Specialty", "Azure Data Engineer Associate", 
                                            "Google Professional Data Engineer", "Databricks Certified Data Engineer", 
                                            "Snowflake SnowPro Core", "Confluent Kafka Developer", "dbt Certified Developer"],
                "tendencias_2025": ["Data Mesh", "Lakehouse Architecture", "Real-time Data Platforms", "Data Contracts", 
                                   "Data Observability", "Data Privacy Engineering", "Metric Stores", "Feature Stores", 
                                   "DataOps", "Semantic Layer", "Data Lineage"]
            },
            "Científico de Datos / Machine Learning Engineer": {
                "tecnologías_clave": ["Python", "R", "SQL", "PyTorch", "TensorFlow", "Keras", "Scikit-learn", "Pandas", "NumPy", 
                                     "Matplotlib", "Hugging Face", "MLflow", "Kubeflow", "DVC", "Databricks", "Weights & Biases", 
                                     "DVC", "JAX", "ONNX", "Ray", "FastAPI", "Luigi"],
                "habilidades_técnicas": ["deep learning", "NLP", "computer vision", "reinforcement learning", "MLOps", 
                                        "feature engineering", "análisis estadístico", "modelado predictivo", "series temporales", 
                                        "optimización de hiperparámetros", "interpretabilidad de modelos", "ML monitoring"],
                "habilidades_blandas": ["pensamiento crítico", "comunicación de resultados complejos", "visualización de datos", 
                                       "storytelling con datos", "colaboración interdisciplinaria", "ética en IA", 
                                       "traducción de problemas de negocio", "presentaciones ejecutivas"],
                "certificaciones_valoradas": ["AWS Machine Learning Specialty", "TensorFlow Developer Certificate", 
                                            "Microsoft Azure AI Engineer", "Google Cloud Professional ML Engineer", 
                                            "Databricks Certified Machine Learning Professional", "IBM Data Science Professional"],
                "tendencias_2025": ["AutoML", "MLOps", "Responsible AI", "Edge AI", "Few-shot Learning", "Foundation Models", 
                                   "ML Monitoring", "Feature Stores", "Fairness & Bias Mitigation", "Data-centric AI", 
                                   "Energy-efficient AI", "Causal ML"]
            },
            "Administrador de Bases de Datos (DBA)": {
                "tecnologías_clave": ["PostgreSQL", "MySQL", "SQL Server", "Oracle Database", "MongoDB", "Cassandra", "Redis", 
                                     "Elasticsearch", "Neo4j", "Snowflake", "DynamoDB", "Kubernetes", "Docker", "Terraform", 
                                     "Ansible", "Python", "Bash", "Prometheus", "Grafana"],
                "habilidades_técnicas": ["modelado de datos", "optimización de queries", "tuning de bases de datos", "alta disponibilidad", 
                                        "disaster recovery", "seguridad de datos", "escalabilidad", "sharding", "replicación", 
                                        "backups", "monitoreo", "automatización de mantenimiento"],
                "habilidades_blandas": ["resolución de problemas", "comunicación técnica clara", "gestión de crisis", 
                                       "planificación de capacidad", "trabajo bajo presión", "documentación detallada"],
                "certificaciones_valoradas": ["Oracle Certified Professional", "Microsoft Certified: Azure Database Administrator Associate", 
                                            "AWS Database Specialty", "MongoDB Professional", "PostgreSQL Associate Certification", 
                                            "EDB PostgreSQL 12 Associate"],
                "tendencias_2025": ["Autonomous Databases", "Cloud Database Management", "Distributed SQL", "Database DevOps", 
                                   "Multi-model Databases", "Database-as-a-Service", "Database Observability", "Database Mesh"]
            },
            "Arquitecto de Software": {
                "tecnologías_clave": ["Microservicios", "Serverless", "Kubernetes", "Docker", "Event-driven Architecture", 
                                     "GraphQL", "REST", "gRPC", "Kafka", "Redis", "AWS", "Azure", "GCP", "Terraform", 
                                     "Prometheus", "Grafana", "Istio", "Envoy", "Linkerd"],
                "habilidades_técnicas": ["diseño de sistemas distribuidos", "patrones de diseño", "arquitectura limpia", 
                                        "arquitectura hexagonal", "modelado de dominio", "DDD", "event sourcing", "CQRS", 
                                        "infraestructura como código", "observabilidad", "resiliencia", "escalabilidad"],
                "habilidades_blandas": ["pensamiento sistémico", "comunicación técnica avanzada", "liderazgo técnico", "mentoría", 
                                       "gestión de stakeholders", "negociación técnica", "visión estratégica"],
                "certificaciones_valoradas": ["AWS Solutions Architect Professional", "Azure Solutions Architect Expert", 
                                            "Google Professional Cloud Architect", "TOGAF", "Certified Kubernetes Architect", 
                                            "Red Hat Certified Architect"],
                "tendencias_2025": ["Composable Architecture", "Microfrontends", "eBPF", "WebAssembly", "Service Mesh", 
                                   "Edge Computing", "GitOps", "Platform Engineering", "Developer Experience", "Green Software"]
            },
            "Ingeniero de Redes": {
                "tecnologías_clave": ["SD-WAN", "SDN", "Cisco", "Juniper", "Arista", "Palo Alto Networks", "FortiGate", 
                                     "BGP", "OSPF", "MPLS", "VPN", "IPsec", "SD-LAN", "Terraform", "Ansible", "AWS VPC", 
                                     "Azure Virtual Network", "GCP VPC", "ZTP", "SASE"],
                "habilidades_técnicas": ["diseño de redes", "configuración de routers y switches", "seguridad perimetral", 
                                        "detección de intrusos", "monitoreo de redes", "troubleshooting", "automatización de redes", 
                                        "NAT", "firewalls", "balanceo de carga", "cloud networking"],
                "habilidades_blandas": ["pensamiento analítico", "resolución de problemas", "comunicación técnica clara", 
                                       "trabajar bajo presión", "documentación detallada", "planificación"],
                "certificaciones_valoradas": ["CCNP", "CCIE", "Juniper JNCIE", "CompTIA Network+", "AWS Advanced Networking Specialty", 
                                            "Azure Network Engineer Associate", "Certified Network Defender"],
                "tendencias_2025": ["Network Automation", "Network as Code", "Zero Trust Networking", "IBN (Intent-Based Networking)", 
                                   "NetSecOps", "AI for Network Operations", "SASE", "Network Observability", "5G Private Networks"]
            },
            "Desarrollador de Aplicaciones Móviles": {
                "tecnologías_clave": ["Swift", "Kotlin", "SwiftUI", "Jetpack Compose", "Flutter", "React Native", "Dart", 
                                     "TypeScript", "GraphQL", "Firebase", "AWS Amplify", "AppSync", "Realm", "Core ML", 
                                     "ARKit", "TensorFlow Lite", "CI/CD Mobile", "Fastlane"],
                "habilidades_técnicas": ["arquitectura limpia para móvil", "responsive design", "gestión de estado", 
                                        "optimización de rendimiento", "diseño UX móvil", "patrones de arquitectura móvil", 
                                        "animaciones", "gestión de memoria", "sincronización offline", "accesibilidad"],
                "habilidades_blandas": ["atención al detalle", "comunicación visual", "empatía con el usuario", 
                                       "colaboración con diseñadores", "feedback constructivo", "documentación clara"],
                "certificaciones_valoradas": ["Google Associate Android Developer", "App Developer with Swift Certification", 
                                            "Flutter Developer Certification", "React Native Certification", "AWS Mobile Developer"],
                "tendencias_2025": ["Super Apps", "App Clips/Instant Apps", "AR/VR en móvil", "On-device AI", "Foldable Experiences", 
                                   "Privacy-first Development", "AppOps", "Sustainable Apps", "Mobile DevSecOps", "Edge Computing"]
            },
            "Ingeniero de Inteligencia Artificial / Deep Learning": {
                "tecnologías_clave": ["PyTorch", "TensorFlow", "JAX", "Hugging Face", "LangChain", "CUDA", "OpenCV", 
                                     "ONNX", "MLflow", "DVC", "Weights & Biases", "Ray", "Kubeflow", "Prometheus", "Docker", 
                                     "Kubernetes", "SageMaker", "Vertex AI", "Azure ML"],
                "habilidades_técnicas": ["deep learning", "NLP", "transformers", "RAG", "fine-tuning de LLMs", "computer vision", 
                                        "MLOps", "reinforcement learning", "GANs", "diffusion models", "redes neuronales", 
                                        "transfer learning", "distributed training", "data-centric AI", "edge AI"],
                "habilidades_blandas": ["pensamiento crítico", "investigación", "comunicación de conceptos técnicos", 
                                       "ética en IA", "resolución creativa de problemas", "mantenerse actualizado"],
                "certificaciones_valoradas": ["Deep Learning Specialization (Coursera)", "TensorFlow Developer Certificate", 
                                            "AWS Machine Learning Specialty", "Google ML Engineer", "NVIDIA DLI", 
                                            "IBM AI Engineering Professional Certificate"],
                "tendencias_2025": ["Multi-modal AI", "Generative AI Agents", "AI Alignment", "Explainable AI", "Efficient Fine-tuning", 
                                   "Foundation Models", "AI Reasoning", "Edge AI at Scale", "Green AI", "Vector Databases"]
            },
            "Ingeniero Cloud": {
                "tecnologías_clave": ["AWS", "Azure", "GCP", "Kubernetes", "Terraform", "CloudFormation", "Pulumi", 
                                     "Docker", "Helm", "Ansible", "GitHub Actions", "Jenkins", "Prometheus", "Grafana", 
                                     "Istio", "Envoy", "Cilium", "ArgoCD", "Flux"],
                "habilidades_técnicas": ["infraestructura como código", "automatización cloud", "multi-cloud", "cloud-native", 
                                        "arquitectura serverless", "seguridad en la nube", "optimización de costos", 
                                        "redes cloud", "observabilidad", "cloud FinOps", "disaster recovery"],
                "habilidades_blandas": ["aprendizaje continuo", "pensamiento arquitectónico", "comunicación interdepartamental", 
                                       "gestión de costos", "documentación", "trabajo en equipo remoto"],
                "certificaciones_valoradas": ["AWS Solutions Architect", "Azure Administrator", "Google Cloud Architect", 
                                            "Certified Kubernetes Administrator", "HashiCorp Terraform Associate", 
                                            "Cloud Security Alliance CCSK"],
                "tendencias_2025": ["FinOps", "Multi-cloud Management", "Cloud Developer Platforms", "Hybrid Cloud", 
                                   "Edge Cloud", "GitOps", "Infrastructure as Code 2.0", "Policy as Code", "Cloud Native Security"]
            },
            "Ingeniero de Pruebas Automatizadas": {
                "tecnologías_clave": ["Selenium", "Cypress", "Playwright", "Jest", "Pytest", "JUnit", "TestNG", "Appium", 
                                     "Postman", "REST Assured", "Gatling", "JMeter", "K6", "Cucumber", "BDD", "Docker", 
                                     "Jenkins", "GitHub Actions", "TestRail", "Jira"],
                "habilidades_técnicas": ["shift-left testing", "TDD", "BDD", "pruebas de regresión", "pruebas de integración", 
                                        "pruebas de API", "pruebas de rendimiento", "pruebas de seguridad", "automatización continua", 
                                        "pruebas en la nube", "pruebas paralelas", "pruebas en microservicios"],
                "habilidades_blandas": ["atención al detalle", "pensamiento crítico", "comunicación de errores", 
                                       "mejora continua", "perspectiva de usuario", "trabajo multidisciplinar"],
                "certificaciones_valoradas": ["ISTQB", "Certified Selenium Professional", "AWS Certified Developer", 
                                            "Azure DevOps Engineer Expert", "Appium Mobile Tester", "ASTQB Mobile Tester"],
                "tendencias_2025": ["AI-assisted Testing", "Testing as Code", "No-code Test Automation", "Visual Testing", 
                                   "Chaos Engineering", "Contract Testing", "Quality Engineering", "Shift-Right Testing", 
                                   "Test Environment as a Service", "Testing in Production"]
            },
            "Consultor en Arquitectura Cloud": {
                "tecnologías_clave": ["AWS", "Azure", "GCP", "Multi-cloud", "Terraform", "CloudFormation", "Kubernetes", 
                                     "Docker", "Serverless", "Event-driven", "Microservicios", "Service Mesh", "API Gateway", 
                                     "Zero Trust", "SASE", "Grafana", "DataDog"],
                "habilidades_técnicas": ["arquitectura de soluciones", "diseño de sistemas distribuidos", "migración a la nube", 
                                        "optimización de costos", "análisis comparativo cloud", "seguridad cloud", "escalabilidad", 
                                        "alta disponibilidad", "disaster recovery", "well-architected framework"],
                "habilidades_blandas": ["comunicación ejecutiva", "gestión de stakeholders", "pensamiento estratégico", 
                                       "negociación", "presentaciones efectivas", "orientación al cliente", "empatía"],
                "certificaciones_valoradas": ["AWS Solutions Architect Professional", "Azure Solutions Architect Expert", 
                                            "Google Professional Cloud Architect", "TOGAF", "Certified Cloud Security Professional", 
                                            "Cloud Native Computing Foundation CNCF"],
                "tendencias_2025": ["FinOps", "Cloud Center of Excellence", "Cloud Security Posture", "Cloud Governance", 
                                   "Multi-cloud Strategy", "Sustainability in Cloud", "Edge Cloud", "Sovereign Cloud"]
            },
            "Administrador de Sistemas Linux/Unix": {
                "tecnologías_clave": ["Linux (RHEL, Ubuntu, Debian)", "Bash", "Python", "Ansible", "Terraform", "Docker", 
                                     "Kubernetes", "Podman", "Prometheus", "Grafana", "ELK Stack", "AWS EC2", "Azure VMs", 
                                     "Git", "SystemD", "LDAP", "SELinux", "firewalld"],
                "habilidades_técnicas": ["administración de servidores", "automatización de infraestructura", "seguridad de sistemas", 
                                        "gestión de parches", "networking", "almacenamiento", "backup & restore", "performance tuning", 
                                        "troubleshooting", "monitoring", "logging", "IAM"],
                "habilidades_blandas": ["resolución de problemas", "comunicación técnica", "trabajo bajo presión", 
                                       "documentación detallada", "disponibilidad", "gestión de prioridades"],
                "certificaciones_valoradas": ["Red Hat Certified Engineer (RHCE)", "Red Hat Certified System Administrator (RHCSA)", 
                                            "Linux Foundation Certified Engineer", "CompTIA Linux+", "AWS SysOps Administrator", 
                                            "Azure Administrator Associate"],
                "tendencias_2025": ["Automatización de sistemas", "Configuración como código", "SRE", "GitOps", "Container-native Linux", 
                                   "Observabilidad", "Linux Security Modules", "Immutable Infrastructure", "AIops"]
            },
            "Especialista en Blockchain": {
                "tecnologías_clave": ["Ethereum", "Solidity", "Rust", "Polkadot", "Binance Smart Chain", "Solana", "NEAR", 
                                     "Web3.js", "Ethers.js", "Hardhat", "Truffle", "Ganache", "IPFS", "Chainlink", "OpenZeppelin", 
                                     "MetaMask", "The Graph", "ZK-Rollups", "Optimistic Rollups"],
                "habilidades_técnicas": ["desarrollo de smart contracts", "tokenomics", "DeFi", "seguridad blockchain", 
                                        "auditoría de contratos", "arquitectura de dApps", "L2 scaling", "interoperabilidad blockchain", 
                                        "cryptography", "consensus mechanisms", "NFTs", "zero-knowledge proofs"],
                "habilidades_blandas": ["pensamiento innovador", "investigación", "explicación de conceptos complejos", 
                                       "pensamiento crítico", "aprendizaje continuo", "comunidad open source"],
                "certificaciones_valoradas": ["Certified Blockchain Developer", "Certified Ethereum Developer", 
                                            "Blockchain Council Certification", "Consensys Academy Bootcamp", 
                                            "Certificate in Applied Cryptography", "Web3 Foundation Certification"],
                "tendencias_2025": ["ZK-Rollups", "Sustainable Blockchain", "Interoperabilidad Web3", "Blockchain for Enterprises", 
                                   "DeFi 2.0", "Real-world Asset Tokenization", "Cross-chain Security", "Identity Solutions", 
                                   "Blockchain Privacy Solutions"]
            },
            "Ingeniero de Automatización": {
                "tecnologías_clave": ["Python", "Bash", "Ansible", "Terraform", "Puppet", "Chef", "Jenkins", "GitLab CI", 
                                     "GitHub Actions", "Circle CI", "Docker", "Kubernetes", "Robot Framework", "Selenium", 
                                     "AWS CDK", "Pulumi", "PowerShell", "UiPath", "Blue Prism"],
                "habilidades_técnicas": ["infraestructura como código", "CI/CD", "DevOps", "scripting", "RPA", "testing automatizado", 
                                        "monitoreo automático", "flujos de trabajo automatizados", "gestión de configuración", 
                                        "orchestration", "event-driven automation", "self-healing systems"],
                "habilidades_blandas": ["pensamiento lógico", "resolución de problemas", "documentación detallada", 
                                       "análisis de procesos", "comunicación interdepartamental", "mejora continua"],
                "certificaciones_valoradas": ["Red Hat Certified Specialist in Ansible Automation", "AWS Developer Associate", 
                                            "Puppet Professional", "UiPath Certified Professional", "HashiCorp Terraform Associate", 
                                            "GitLab Professional"],
                "tendencias_2025": ["NoCode/LowCode Automation", "GitOps", "Serverless Automation", "AI-augmented Automation", 
                                   "Event-driven Automation", "Self-service Automation", "Hyper-automation", "Cross-platform Automation"]
            },
            "Desarrollador Front-End": {
                "tecnologías_clave": ["React", "Next.js", "Vue", "Nuxt", "Angular", "Svelte", "TypeScript", "JavaScript", 
                                     "TailwindCSS", "Styled Components", "GraphQL", "REST", "Redux", "Zustand", "React Query", 
                                     "Testing Library", "Cypress", "Storybook", "Webpack", "Vite"],
                "habilidades_técnicas": ["optimización de rendimiento", "responsive design", "accesibilidad (WCAG)", 
                                        "arquitectura de front-end", "SSR/SSG", "PWA", "microfrontends", "web vitals", 
                                        "interacción API", "state management", "web animations", "SEO técnico"],
                "habilidades_blandas": ["atención al detalle", "colaboración con diseñadores", "empatía con usuarios", 
                                       "resolución creativa de problemas", "comunicación visual", "trabajo en equipo"],
                "certificaciones_valoradas": ["Meta Front-End Developer Professional Certificate", "Google UX Design Professional Certificate", 
                                            "W3Schools Front End Certification", "freeCodeCamp Certification", 
                                            "JavaScript Certification", "OpenJS Foundation Certification"],
                "tendencias_2025": ["Web Components", "Edge rendering", "WebAssembly", "JAMstack", "Core Web Vitals", "Headless CMS", 
                                   "Design Systems", "Island Architecture", "Partial Hydration", "Streaming Server Components"]
            },
            "Ingeniero de Integración / API": {
                "tecnologías_clave": ["REST", "GraphQL", "gRPC", "WebSockets", "Apache Kafka", "RabbitMQ", "Apigee", "Kong", 
                                     "Tyk", "AWS API Gateway", "Azure API Management", "Postman", "Swagger/OpenAPI", "Mulesoft", 
                                     "Apache Camel", "Zapier", "Terraform", "Kubernetes"],
                "habilidades_técnicas": ["diseño de APIs", "middleware", "ESB", "patrones de integración", "protocols (HTTP, MQTT, AMQP)", 
                                        "API management", "API testing", "API security", "API documentation", "webhooks", 
                                        "streaming de datos", "batch processing", "EAI"],
                "habilidades_blandas": ["comunicación interdepartamental", "documentación técnica", "solución de problemas", 
                                       "pensamiento sistémico", "gestión de stakeholders", "negociación"],
                "certificaciones_valoradas": ["MuleSoft Certified Developer", "Kong Certified Developer", "AWS API Gateway", 
                                            "Microsoft Azure API Management", "Apigee API Engineer", "Postman API Certification"],
                "tendencias_2025": ["API-first Design", "API Governance", "API Federation", "GraphQL Federation", "Event-driven APIs", 
                                   "API Analytics", "Zero Trust API", "API SBOM", "Declarative API Systems", "MACH Architecture"]
            },
            "Ingeniero de Big Data": {
                "tecnologías_clave": ["Spark", "Hadoop", "Hive", "Kafka", "Flink", "AWS EMR", "Databricks", "Snowflake", 
                                     "Redshift", "BigQuery", "Delta Lake", "dbt", "Airflow", "NiFi", "Kubernetes", "Docker", 
                                     "Python", "Scala", "SQL", "HBase", "Presto", "Trino"],
                "habilidades_técnicas": ["ingeniería de datos distribuidos", "procesamiento batch/streaming", "data lakehouse", 
                                        "ETL/ELT", "modelado dimensional", "optimización de consultas", "data governance", 
                                        "data quality", "particionamiento de datos", "escalabilidad", "ingeniería de features"],
                "habilidades_blandas": ["pensamiento analítico", "resolución de problemas complejos", "documentación técnica",
                                       "comunicación interdepartamental", "trabajo con stakeholders", "capacidad de abstracción"],
                "certificaciones_valoradas": ["AWS Data Analytics Specialty", "Cloudera Certified Professional", 
                                            "Databricks Certified Data Engineer", "Google Professional Data Engineer", 
                                            "Microsoft Certified: Azure Data Engineer", "Snowflake SnowPro Core"],
                "tendencias_2025": ["Data Mesh", "Data Contracts", "Real-time Analytics", "Streaming-first Architecture", 
                                   "Lakehouse", "Metric Layers", "Feature Stores", "Data Products", "Federated Governance"]
            },
            "Ingeniero IoT": {
                "tecnologías_clave": ["Arduino", "Raspberry Pi", "ESP32", "MQTT", "CoAP", "LoRaWAN", "Zigbee", "BLE", 
                                     "AWS IoT", "Azure IoT", "Google Cloud IoT", "Node-RED", "TensorFlow Lite", 
                                     "EdgeX Foundry", "Mosquitto", "Docker", "Kubernetes", "Python", "C/C++"],
                "habilidades_técnicas": ["edge computing", "embedded systems", "conectividad inalámbrica", "seguridad IoT", 
                                        "protocolos de comunicación", "procesamiento de señales", "analytics en tiempo real", 
                                        "diseño de PCB", "on-device AI", "computación distribuida", "edge-to-cloud"],
                "habilidades_blandas": ["pensamiento analítico", "resolución de problemas", "pensamiento creativo", 
                                       "comunicación interdisciplinaria", "atención al detalle", "seguridad by design"],
                "certificaciones_valoradas": ["AWS IoT Specialty", "Microsoft Certified: Azure IoT Developer", 
                                            "IoT Certified Professional", "Certified IoT Security Practitioner", 
                                            "Cisco IoT Certification", "CompTIA IoT Practitioner"],
                "tendencias_2025": ["Digital Twins", "IoT + AI/ML", "Edge Intelligence", "5G IoT", "Quantum IoT Security", 
                                   "Energy Harvesting", "IoT Swarm Intelligence", "IT/OT Convergence", "Advanced Embedded ML"]
            }
        }           
        
        
        # Patrones comunes de faltantes en CVs
        self.patrones_deteccion = {
            "linkedin_faltante": r'linkedin\.com\/in\/[a-zA-Z0-9\-]+',
            "github_faltante": r'github\.com\/[a-zA-Z0-9\-]+',
            "logros_cuantificables": r'aument[óo]\s+\d+%|reduj[oe]\s+\d+%|ahorr[óo]\s+\d+|mejor[óo]\s+\d+%|optimiz[eé]\s+\d+|increment[eé]\s+\d+',
            "certificaciones": r'certifica(do|ción)|diploma|acredita(do|ción)|título|curso|capacitaci[oó]n',
            "idiomas": r'ingl[ée]s|franc[ée]s|alem[aá]n|italiano|chino|japon[ée]s|portugu[ée]s|nivel\s+[A-C][1-2]|fluidez',
            "habilidades_blandas": r'liderazgo|trabajo\s+en\s+equipo|comunicaci[oó]n|resoluci[oó]n\s+de\s+problemas|adaptabilidad|creativ[oa]|colabora(tivo|ción)|iniciativa|proactiv[oa]|orientad[oa]\s+a\s+',
            "formacion_continua": r'curso|capacitaci[oó]n|taller|seminario|actualizaci[oó]n|formaci[oó]n\s+continua|bootcamp|MOOC|autodidacta|aprendizaje\s+continuo',
            "estructura_proyecto": r'responsabilidades|logros|tecnolog[ií]as\s+utilizadas|metodolog[ií]a|resultados|objetivos|colaboraci[oó]n',
            "fechas_experiencia": r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}|(\d{1,2}\/\d{4})|(\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*(presente|actualidad|hoy))',
            "educacion_detallada": r'universidad|instituto|grado|título|graduado|licenciado|ingeniero|máster|doctorado|especialización|técnico|superior|bachiller|diplomado',
            "portafolio_proyectos": r'portafolio|proyectos?\s+personales|proyectos?\s+destacados|repositorio|demo|sitio\s+web|aplicaci[oó]n',
            "voluntariado": r'voluntario|voluntariado|ad\s+honorem|pro\s+bono|sin\s+fines\s+de\s+lucro|ONG|social|comunidad',
            "referencias": r'referencias|referentes|contactos\s+profesionales',
            "perfil_profesional": r'perfil\s+profesional|resumen\s+profesional|objetivo\s+profesional|acerca\s+de\s+mí|sobre\s+mí|presentación',
            "habilidades_técnicas": r'habilidades\s+t[eé]cnicas|competencias\s+t[eé]cnicas|conocimientos\s+t[eé]cnicos|skills|tecnolog[ií]as|herramientas'
        }
        
        # Plantillas de recomendaciones genéricas por categoría
        self.recomendaciones_personalizadas = {
            "linkedin_faltante": [
                "Incluye tu perfil de LinkedIn personalizado para aumentar tu visibilidad profesional en el sector de {puesto}. Los reclutadores técnicos consultan activamente LinkedIn para validar experiencia y habilidades específicas.",
                "Añade una URL personalizada de LinkedIn (linkedin.com/in/tunombre) ya que el 87% de los reclutadores en tecnología verifican los perfiles profesionales. Para roles de {puesto}, esto puede ser un diferenciador clave en el proceso de selección.",
                "Integra tu perfil de LinkedIn completo y actualizado, destacando tu experiencia con {tech_ejemplo}. Los profesionales de {puesto} con perfiles de LinkedIn optimizados reciben hasta un 40% más de oportunidades según estudios recientes."
            ],
            "github_faltante": [
                "Incorpora enlaces a tus repositorios de GitHub que muestren proyectos con {tech_ejemplo}. Para un puesto de {puesto}, es fundamental demostrar experiencia práctica con código real, especialmente en proyectos relacionados con {area_tech}.",
                "Añade tu perfil de GitHub destacando contribuciones a proyectos open source o personales que utilicen {tech_ejemplo}. Los empleadores buscan {puesto} con evidencia tangible de sus habilidades, no solo menciones en el CV.",
                "Incluye un enlace a tu GitHub con repositorios de proyectos prácticos para validar tu experiencia con {tech_ejemplo}. Más del 70% de los reclutadores técnicos para puestos de {puesto} revisan código de los candidatos antes de entrevistarlos."
            ],
            "logros_cuantificables": [
                "Transforma tus descripciones de responsabilidades en logros medibles. Por ejemplo, en lugar de 'Desarrollé con {tech_ejemplo}', especifica 'Implementé {tech_ejemplo} reduciendo en un 40% el tiempo de respuesta y mejorando la experiencia de usuario en un 35%'.",
                "Incorpora métricas específicas en tus logros con {tech_ejemplo}. Los reclutadores para {puesto} buscan resultados concretos como 'Rediseñé la arquitectura utilizando {tech_ejemplo}, logrando una reducción del 30% en costos de infraestructura y un aumento del 25% en velocidad'.",
                "Cuantifica el impacto de tu trabajo con {tech_ejemplo} utilizando KPIs relevantes. Por ejemplo: 'Lideré la migración a {tech_ejemplo} que redujo un 45% los tiempos de despliegue y mejoró la estabilidad del sistema en un 60%, eliminando el 90% de incidentes nocturnos'."
            ],
            "certificaciones": [
                "Destaca certificaciones relevantes para {puesto} como {cert_ejemplo} y {cert_ejemplo2}. Estas validaciones técnicas específicas pueden aumentar hasta un 30% tus posibilidades de ser considerado para entrevistas según estudios del sector.",
                "Añade una sección dedicada a tus certificaciones en {tech_ejemplo} o {cert_ejemplo}, priorizando las más reconocidas en la industria. Para roles de {puesto}, estas credenciales verifican tu conocimiento especializado y compromiso profesional.",
                "Complementa tu formación con certificaciones específicas del sector como {cert_ejemplo}. Para posiciones de {puesto} que trabajan con {tech_ejemplo}, estas acreditaciones son altamente valoradas e incluso requeridas por algunas empresas líderes."
            ],
            "idiomas": [
                "Especifica tus niveles de idiomas según el Marco Común Europeo (A1-C2), enfatizando especialmente tu nivel de inglés técnico. Para roles de {puesto} que trabajan con {tech_ejemplo}, la capacidad de leer documentación y participar en comunidades internacionales es esencial.",
                "Detalla tus competencias lingüísticas con precisión (nivel conversacional, profesional, nativo). En entornos de desarrollo con {tech_ejemplo}, el inglés técnico fluido es particularmente valorado para la colaboración en equipos distribuidos globalmente.",
                "Incluye una sección clara de idiomas que especifique tu nivel en cada uno (B2, C1, etc.). Los roles de {puesto} frecuentemente requieren comunicación con equipos internacionales y comprensión de documentación técnica actualizada en inglés sobre {tech_ejemplo}."
            ],
            "habilidades_blandas": [
                "Complementa tus conocimientos técnicos de {tech_ejemplo} con habilidades blandas relevantes para {puesto}, como {soft_skill} y {soft_skill2}. Contextualiza estas aptitudes con ejemplos concretos de su aplicación en proyectos técnicos.",
                "Incluye competencias transversales específicas valoradas para {puesto}, como {soft_skill} en entornos ágiles y {soft_skill2}. Estudios recientes muestran que el 67% de los empleadores priorizan estas habilidades junto con el conocimiento técnico de {tech_ejemplo}.",
                "Equilibra tu perfil técnico con habilidades blandas estratégicas para {puesto}, particularmente {soft_skill} y {soft_skill2}. Describe brevemente cómo aplicaste estas competencias para mejorar proyectos con {tech_ejemplo} y lograr resultados superiores."
            ],
            "formacion_continua": [
                "Destaca tu aprendizaje continuo en {tech_ejemplo} y {tech_emergente} mediante cursos especializados o certificaciones. Para roles de {puesto}, demostrar actualización constante en tecnologías emergentes como {tech_emergente} es un diferenciador clave.",
                "Añade una sección de formación continua que muestre tu actualización en {tech_ejemplo} y tendencias emergentes como {tech_emergente}. Los empleadores de {puesto} valoran candidatos que se mantienen al día con la evolución tecnológica del sector.",
                "Incluye cursos recientes, bootcamps o proyectos de aprendizaje relacionados con {tech_ejemplo} y tecnologías emergentes como {tech_emergente}. Esto demuestra tu compromiso con mantenerte relevante en un campo tan dinámico como {puesto}."
            ],
            "estructura_proyecto": [
                "Estructura cada experiencia con {tech_ejemplo} siguiendo el formato: contexto del proyecto → desafíos técnicos → soluciones implementadas → tecnologías utilizadas ({tech_ejemplo}) → resultados cuantificables. Esta claridad facilita la evaluación de tu perfil para posiciones de {puesto}.",
                "Organiza tus proyectos con {tech_ejemplo} con una estructura consistente: problema de negocio → arquitectura técnica implementada → metodología utilizada → stack tecnológico (destacando {tech_ejemplo}) → métricas de éxito. Esta presentación permite comprender rápidamente tu impacto como {puesto}.",
                "Detalla tus experiencias con {tech_ejemplo} mediante una estructura clara: objetivo del proyecto → responsabilidades específicas → tecnologías clave implementadas → retos superados → resultados medibles. Esta organización resalta tu capacidad para resolver problemas como {puesto}."
            ],
            "fechas_experiencia": [
                "Especifica cronológicamente cada posición con fechas precisas (MM/AAAA) para todas tus experiencias con {tech_ejemplo}. Los sistemas de seguimiento de candidatos (ATS) para {puesto} filtran a menudo por duración y actualidad de la experiencia relevante.",
                "Detalla con exactitud los períodos de trabajo (enero 2023 - presente) en cada rol, especialmente donde utilizaste {tech_ejemplo}. Para posiciones de {puesto}, la secuencia temporal clara ayuda a evaluar tu progresión técnica y experiencia acumulada.",
                "Incluye cronología precisa para cada experiencia profesional, indicando meses y años. Los reclutadores para {puesto} analizan esta información para verificar continuidad y evaluar tu experiencia reciente con tecnologías como {tech_ejemplo}."
            ],
            "educacion_detallada": [
                "Expande los detalles de tu formación académica relacionada con {puesto}, mencionando proyectos finales o investigaciones relevantes sobre {tech_ejemplo}. Incluye el nombre exacto de tu titulación y especialización más relevante para el puesto.",
                "Detalla tu educación incluyendo asignaturas clave relacionadas con {tech_ejemplo} y proyectos académicos aplicados. Para roles de {puesto}, esto establece una base sólida de conocimientos técnicos fundamentales además de tu experiencia práctica.",
                "Complementa la información de tu formación con menciones a proyectos académicos que utilizaran {tech_ejemplo} u otras tecnologías relevantes para {puesto}. Destaca trabajos de investigación, tesis o proyectos finales directamente aplicables al rol."
            ],
            "palabras_clave": [
                "Incorpora términos técnicos específicos del sector de {puesto} como {tech_ejemplo}, {tech_ejemplo2} y {habilidad_tecnica}. Los sistemas ATS buscan estas palabras clave para filtrar candidatos, y su ausencia puede eliminar CVs cualificados antes de la revisión humana.",
                "Incluye términos técnicos estratégicos como {tech_ejemplo}, {tech_ejemplo2} y metodologías como {habilidad_tecnica}. Para posiciones de {puesto}, estos términos son filtros primarios en sistemas de reclutamiento automatizados.",
                "Añade palabras clave específicas del ecosistema de {tech_ejemplo}, incluyendo frameworks, herramientas y metodologías relacionadas como {tech_ejemplo2} y {habilidad_tecnica}. Esto optimiza tu CV para búsquedas específicas de {puesto}."
            ],
            "actualizacion_tecnologias": [
                "Actualiza tu stack tecnológico para incluir herramientas modernas como {tech_ejemplo}, {tech_ejemplo2} y {tech_emergente}. En el ámbito de {puesto}, estar familiarizado con estas tecnologías emergentes es cada vez más valorado por su impacto en {area_tech}.",
                "Destaca experiencia con tecnologías actuales como {tech_ejemplo} y {tech_ejemplo2}, muy demandadas en roles de {puesto}. Considera añadir familiaridad con {tech_emergente}, ya que está ganando adopción rápidamente en el sector.",
                "Menciona conocimientos en tecnologías emergentes como {tech_emergente} junto a tu experiencia en {tech_ejemplo}. Para posiciones de {puesto} en 2025, estas competencias son diferenciadoras ya que abordan desafíos contemporáneos en {area_tech}."
            ],
            "formato_conciso": [
                "Optimiza tu CV a máximo 2 páginas, priorizando tu experiencia reciente con {tech_ejemplo}. Los reclutadores para {puesto} dedican en promedio 6-7 segundos a la primera revisión, por lo que la concisión y relevancia inmediata son cruciales.",
                "Estructura tu información de forma concisa y visual, utilizando viñetas y secciones claras para destacar tus logros con {tech_ejemplo}. La optimización del espacio facilita que los puntos clave para {puesto} sean identificados rápidamente.",
                "Condensa tu información manteniendo únicamente lo más relevante para {puesto}, especialmente tu experiencia con {tech_ejemplo} y tecnologías relacionadas. Utiliza frases directas con verbos de acción y elimina repeticiones para maximizar el impacto."
            ],
            "experiencia_relevante": [
                "Prioriza y expande tus roles relacionados con {puesto}, especialmente aquellos donde utilizaste {tech_ejemplo}. Dedica 3-4 viñetas a estas experiencias mientras reduces a 1-2 para posiciones menos relevantes, creando una narrativa dirigida al puesto objetivo.",
                "Destaca prominentemente tu experiencia con {tech_ejemplo} y {tech_ejemplo2}, reorganizando tu CV para que las responsabilidades más relevantes para {puesto} aparezcan primero en cada posición, incluso si no eran tus tareas principales.",
                "Enfatiza los proyectos que demuestren competencias directamente transferibles al rol de {puesto}, particularmente aquellos con {tech_ejemplo}. Reescribe tus experiencias menos relevantes para destacar aspectos que aún puedan relacionarse con el puesto objetivo."
            ],
            "portafolio": [
                "Crea y añade un enlace a un portafolio digital que muestre en detalle tus proyectos con {tech_ejemplo}. Para roles de {puesto}, poder visualizar tu trabajo práctico puede ser decisivo, especialmente con ejemplos de implementaciones de {area_tech}.",
                "Incluye un portafolio técnico en línea con casos de estudio de tus implementaciones de {tech_ejemplo}. Los reclutadores para {puesto} valoran poder examinar ejemplos concretos de tu enfoque para resolver problemas en {area_tech}.",
                "Complementa tu CV con un portafolio que demuestre tus habilidades con {tech_ejemplo} en situaciones reales. Incluye capturas de interfaces, diagramas de arquitectura o ejemplos de código (anonimizados) para validar tu experiencia práctica en {area_tech}."
            ],
            "tendencias_actuales": [
                "Incorpora experiencia o conocimiento en tendencias actuales como {tendencia_reciente} y {tendencia_reciente2}. Para un rol de {puesto} en 2025, la familiaridad con estas innovaciones demuestra tu visión estratégica y capacidad de anticipación.",
                "Menciona tu interés o experiencia en tendencias emergentes como {tendencia_reciente} aplicada a {tech_ejemplo}. Los empleadores buscan profesionales de {puesto} que comprendan hacia dónde evoluciona el sector.",
                "Destaca cualquier proyecto o formación relacionada con {tendencia_reciente}, incluso si es a nivel experimental o de autoestudio. Para roles de {puesto}, estar al tanto de innovaciones como {tendencia_reciente2} te posiciona como un profesional progresista."
            ]
        }
        
        # Prepara el vectorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 3),
            stop_words=['de', 'la', 'el', 'en', 'y', 'a', 'con', 'para', 'por', 'del', 'los', 'las', 'un', 'una', 'lo']
        )
    
    def _detectar_faltantes(self, texto_cv: str) -> Dict[str, bool]:
        """Detecta elementos faltantes en el CV usando expresiones regulares"""
        resultados = {}
        for nombre, patron in self.patrones_deteccion.items():
            resultados[nombre] = len(re.findall(patron, texto_cv.lower())) == 0
        return resultados
    
    def _extraer_tech_stack(self, texto_cv: str, puesto: str) -> Dict[str, Set[str]]:
        """Extrae tecnologías y habilidades mencionadas en el CV"""
        texto_lower = texto_cv.lower()
        
        # Identificar la categoría de puesto más relevante
        categoria_puesto = self._identificar_categoria_puesto(puesto)
        
        # Extraer tecnologías por categoría
        mencionadas = {}
        conocimiento_puesto = self.conocimiento_puesto.get(categoria_puesto, {})
        
        for categoria, keywords in conocimiento_puesto.items():
            if isinstance(keywords, list):
                mencionadas[categoria] = set()
                for keyword in keywords:
                    if keyword.lower() in texto_lower:
                        mencionadas[categoria].add(keyword)
        
        return mencionadas
    
    def _identificar_categoria_puesto(self, puesto: str) -> str:
        """Identifica la categoría de puesto más relevante"""
        # Buscar coincidencia exacta
        for categoria in self.conocimiento_puesto.keys():
            if categoria.lower() == puesto.lower():
                return categoria
        
        # Buscar coincidencia parcial
        for categoria in self.conocimiento_puesto.keys():
            if categoria.lower() in puesto.lower() or puesto.lower() in categoria.lower():
                return categoria
            
            # Comparar palabras clave
            palabras_puesto = set(puesto.lower().split())
            palabras_categoria = set(categoria.lower().split())
            if len(palabras_puesto.intersection(palabras_categoria)) > 0:
                return categoria
        
        # Si no hay coincidencias, usar una categoría por defecto basada en palabras clave
        if "desarrollador" in puesto.lower() or "programador" in puesto.lower():
            return "Desarrollador Full Stack"
        elif "datos" in puesto.lower() or "data" in puesto.lower():
            return "Ingeniero de Datos"
        elif "cloud" in puesto.lower() or "nube" in puesto.lower():
            return "Ingeniero Cloud"
        elif "seguridad" in puesto.lower() or "security" in puesto.lower():
            return "Especialista en Ciberseguridad"
        elif "devops" in puesto.lower():
            return "Ingeniero DevOps"
        elif "ia" in puesto.lower() or "ml" in puesto.lower() or "machine learning" in puesto.lower():
            return "Ingeniero de Inteligencia Artificial / Deep Learning"
        else:
            # Default
            return "Desarrollador Full Stack"
    
    def _analizar_relevancia_para_puesto(self, tech_mencionadas: Dict[str, Set[str]], puesto: str) -> Dict[str, float]:
        """Analiza la relevancia del CV para el puesto específico basado en tecnologías"""
        categoria_puesto = self._identificar_categoria_puesto(puesto)
        conocimiento_puesto = self.conocimiento_puesto.get(categoria_puesto, {})
        
        resultados = {}
        for categoria, keywords in conocimiento_puesto.items():
            if isinstance(keywords, list) and len(keywords) > 0:
                # Calcular porcentaje de keywords presentes
                mencionadas = tech_mencionadas.get(categoria, set())
                relevancia = len(mencionadas) / len(keywords) if len(keywords) > 0 else 0
                resultados[categoria] = relevancia
                
        return resultados
    
    def _analizar_estructura_cv(self, texto_cv: str) -> Dict[str, bool]:
        """Analiza la estructura y formato del CV"""
        secciones_esperadas = {
            "perfil": ["perfil", "sobre mí", "acerca de", "presentación", "resumen", "objective", "summary"],
            "experiencia": ["experiencia", "laboral", "profesional", "trayectoria", "work experience"],
            "educacion": ["educación", "formación", "estudios", "académica", "education"],
            "habilidades": ["habilidades", "competencias", "skills", "conocimientos", "tecnologías", "tech stack"],
            "logros": ["logros", "achievements", "accomplishments", "resultados"],
            "proyectos": ["proyectos", "projects", "portfolio", "repositorios"],
            "contacto": ["contacto", "datos personales", "información personal", "email", "teléfono", "contact"]
        }
        
        resultado = {}
        texto_lower = texto_cv.lower()
        
        # Detectar secciones presentes
        for seccion, keywords in secciones_esperadas.items():
            resultado[seccion] = any(kw in texto_lower for kw in keywords)
            
        # Evaluar formato general
        parrafos = [p for p in texto_cv.split('\n\n') if p.strip()]
        lineas = texto_cv.count('\n') + 1
        palabras = len(re.findall(r'\b\w+\b', texto_cv))
        
        # Criterios de formato óptimo
        resultado["longitud_adecuada"] = 300 <= palabras <= 1200  # Entre 1-2 páginas aprox.
        resultado["formato_escaneable"] = len(parrafos) >= 5 and lineas >= 20  # Suficientes párrafos y líneas
        resultado["parrafos_bien_formados"] = sum(1 for p in parrafos if 20 <= len(p) <= 500) >= len(parrafos) * 0.7
        
        return resultado
    
    def _generar_recomendaciones_avanzadas(self, texto_cv: str, puesto: str) -> List[str]:
    
        # 1. Detectar elementos faltantes
        elementos_faltantes = self._detectar_faltantes(texto_cv)
        
        # 2. Extraer stack tecnológico 
        tech_mencionadas = self._extraer_tech_stack(texto_cv, puesto)
        
        # 3. Analizar relevancia para el puesto
        relevancia = self._analizar_relevancia_para_puesto(tech_mencionadas, puesto)
        
        # 4. Analizar estructura del CV
        estructura = self._analizar_estructura_cv(texto_cv)
        
        # 5. Identificar categoría de puesto específica
        categoria_puesto = self._identificar_categoria_puesto(puesto)
        conocimiento_puesto = self.conocimiento_puesto.get(categoria_puesto, {})
        
        # Generar recomendaciones basadas en análisis
        recomendaciones = []
        
        # 5.1 Recomendaciones por elementos faltantes críticos
        elementos_criticos = ["linkedin_faltante", "github_faltante", "logros_cuantificables", 
                            "certificaciones", "idiomas", "habilidades_blandas", "estructura_proyecto"]
        
        for elemento in elementos_criticos:
            if elementos_faltantes.get(elemento, False):
                # Buscar plantilla personalizada
                plantillas = self.recomendaciones_personalizadas.get(elemento, [])
                if plantillas:
                    # Seleccionar aleatoriamente una plantilla
                    plantilla = random.choice(plantillas)
                    
                    # Personalizar con ejemplos específicos del puesto
                    tech_ejemplos = list(tech_mencionadas.get("tecnologías_clave", set()))
                    if not tech_ejemplos and "tecnologías_clave" in conocimiento_puesto:
                        tech_ejemplos = conocimiento_puesto["tecnologías_clave"][:5]
                    
                    # Crear un diccionario de contexto aquí, antes de usarlo
                    contexto = {
                        "puesto": puesto,
                        "tech_ejemplo": random.choice(tech_ejemplos) if tech_ejemplos else "tecnologías relevantes",
                        "tech_ejemplo2": "",  # Lo estableceremos a continuación si es posible
                        "cert_ejemplo": random.choice(conocimiento_puesto.get("certificaciones_valoradas", ["certificaciones relevantes"])),
                        "cert_ejemplo2": "",  # Lo estableceremos a continuación si es posible
                        "soft_skill": random.choice(conocimiento_puesto.get("habilidades_blandas", ["comunicación efectiva"])),
                        "soft_skill2": "",  # Lo estableceremos a continuación si es posible
                        "tech_emergente": random.choice(conocimiento_puesto.get("tendencias_2025", ["tecnologías emergentes"])),
                        "tendencia_reciente": random.choice(conocimiento_puesto.get("tendencias_2025", ["tendencias actuales"])),
                        "tendencia_reciente2": "",  # Lo estableceremos a continuación si es posible
                        "area_tech": "arquitectura de software" if "arquitecto" in puesto.lower() else "desarrollo de aplicaciones" if "desarrollador" in puesto.lower() else "infraestructura cloud" if "cloud" in puesto.lower() else "seguridad informática" if "seguridad" in puesto.lower() else "análisis de datos" if "datos" in puesto.lower() else "tecnología"
                    }
                    
                    # Ahora establecemos los elementos secundarios si hay suficientes para elegir
                    if len(tech_ejemplos) > 1:
                        contexto["tech_ejemplo2"] = random.choice([t for t in tech_ejemplos if t != contexto["tech_ejemplo"]])
                    
                    cert_ejemplos = conocimiento_puesto.get("certificaciones_valoradas", [])
                    if len(cert_ejemplos) > 1:
                        contexto["cert_ejemplo2"] = random.choice([c for c in cert_ejemplos if c != contexto["cert_ejemplo"]])
                    
                    soft_skills = conocimiento_puesto.get("habilidades_blandas", [])
                    if len(soft_skills) > 1:
                        contexto["soft_skill2"] = random.choice([s for s in soft_skills if s != contexto["soft_skill"]])
                    
                    tendencias = conocimiento_puesto.get("tendencias_2025", [])
                    if len(tendencias) > 1:
                        contexto["tendencia_reciente2"] = random.choice([t for t in tendencias if t != contexto["tendencia_reciente"]])
                    
                    # Formatear la plantilla con el contexto
                    try:
                        recomendacion_personalizada = plantilla.format(**contexto)
                        recomendaciones.append(recomendacion_personalizada)
                    except Exception as e:
                        print(f"Error al formatear plantilla: {str(e)}")
                        continue
    
    # Resto del código...


        # 2. Añadir recomendaciones por relevancia baja
        categorias_bajas = []
        for categoria, puntuacion in relevancia.items():
            if puntuacion < 0.4 and "tecnologías" in categoria:
                # Identificar tecnologías faltantes importantes
                todas_tech = set(conocimiento_puesto.get(categoria, []))
                tech_presentes = tech_mencionadas.get(categoria, set())
                tech_faltantes = todas_tech - tech_presentes
                
                # Seleccionar tecnologías prioritarias
                tech_prioritarias = list(tech_faltantes)[:3]
                if tech_prioritarias:
                    # Generar recomendación sobre tecnologías faltantes
                    plantilla = random.choice(self.recomendaciones_personalizadas.get("actualizacion_tecnologias", []))
                    contexto = {
                        "puesto": puesto,
                        "tech_ejemplo": ", ".join(tech_prioritarias),
                        "tech_emergente": random.choice(conocimiento_puesto.get("tendencias_2025", ["tecnologías emergentes"])),
                        "area_tech": "arquitectura de software" if "arquitecto" in puesto.lower() else "desarrollo de aplicaciones" if "desarrollador" in puesto.lower() else "infraestructura cloud" if "cloud" in puesto.lower() else "seguridad informática" if "seguridad" in puesto.lower() else "análisis de datos" if "datos" in puesto.lower() else "tecnología"
                    }
                    recomendacion = plantilla.format(**contexto)
                    recomendaciones.append(recomendacion)
                    
                categorias_bajas.append(categoria)
        
        # 3. Añadir recomendaciones por estructura inadecuada
        if len(recomendaciones) < 4:
            tendencias = conocimiento_puesto.get("tendencias_2025", [])
            if tendencias:
                plantilla = random.choice(self.recomendaciones_personalizadas.get("tendencias_actuales", []))
                contexto = {
                    "puesto": puesto,
                    "tendencia_reciente": random.choice(tendencias),
                    "tendencia_reciente2": random.choice([t for t in tendencias if t != contexto.get("tendencia_reciente", "")]) if len(tendencias) > 1 else "otras innovaciones del sector",
                    "tech_ejemplo": random.choice(conocimiento_puesto.get("tecnologías_clave", ["tecnologías relevantes"]))
                }
                recomendacion = plantilla.format(**contexto)
                recomendaciones.append(recomendacion)
        
        # 5.4 Recomendaciones de estructura y formato
        if not estructura.get("perfil", True) or not estructura.get("logros", True):
            recomendaciones.append(f"Añade una sección de perfil profesional al inicio del CV que resuma en 3-4 líneas tu experiencia y especialización como {puesto}, destacando tus fortalezas clave y propuesta de valor única.")
            
        if not estructura.get("longitud_adecuada", True) or not estructura.get("parrafos_bien_formados", True):
            plantilla = random.choice(self.recomendaciones_personalizadas.get("formato_conciso", []))
            contexto = {
                "puesto": puesto,
                "tech_ejemplo": random.choice(conocimiento_puesto.get("tecnologías_clave", ["tecnologías relevantes"]))
            }
            recomendacion = plantilla.format(**contexto)
            recomendaciones.append(recomendacion)
            
        # 5.5 Recomendación sobre portafolio para roles técnicos
        if elementos_faltantes.get("portafolio_proyectos", False) and "desarrollador" in puesto.lower() or "ingeniero" in puesto.lower() or "arquitecto" in puesto.lower():
            plantilla = random.choice(self.recomendaciones_personalizadas.get("portafolio", []))
            contexto = {
                "puesto": puesto,
                "tech_ejemplo": random.choice(conocimiento_puesto.get("tecnologías_clave", ["tecnologías relevantes"])),
                "area_tech": "desarrollo de software" if "desarrollador" in puesto.lower() else "arquitectura de sistemas" if "arquitecto" in puesto.lower() else "implementaciones técnicas"
            }
            recomendacion = plantilla.format(**contexto)
            recomendaciones.append(recomendacion)
            
        # Eliminar duplicados y limitar a 7 recomendaciones máximo
        recomendaciones = list(dict.fromkeys(recomendaciones))
        recomendaciones = recomendaciones[:9]
        
        # Si hay pocas recomendaciones, añadir una general sobre relevancia para el puesto
        if len(recomendaciones) < 4:
            plantilla = random.choice(self.recomendaciones_personalizadas.get("experiencia_relevante", []))
            contexto = {
                "puesto": puesto,
                "tech_ejemplo": random.choice(conocimiento_puesto.get("tecnologías_clave", ["tecnologías relevantes"]))
            }
            recomendacion = plantilla.format(**contexto)
            recomendaciones.append(recomendacion)
            
        return recomendaciones
    
    def generar_recomendaciones(self, texto_cv: str, puesto: str) -> List[str]:
        """
        Genera recomendaciones personalizadas y contextuales para mejorar el CV,
        asegurándose de no sugerir elementos que ya están presentes.
        
        Args:
            texto_cv: Texto extraído del CV
            puesto: Puesto al que aplica el usuario
            
        Returns:
            Lista de recomendaciones relevantes y precisas
        """
        try:
            # Normalizar texto para análisis
            texto_lower = texto_cv.lower()
            
            # Identificar categoría de puesto
            categoria_puesto = None
            for key in recommendation_generator.conocimiento_puesto.keys():
                if key.lower() in puesto.lower() or puesto.lower() in key.lower():
                    categoria_puesto = key
                    break
            
            # Si no hay match, usar categoría por defecto
            if not categoria_puesto:
                if "desarrollador" in puesto.lower() or "programador" in puesto.lower():
                    categoria_puesto = "Desarrollador Full Stack"
                elif "datos" in puesto.lower() or "data" in puesto.lower():
                    categoria_puesto = "Ingeniero de Datos"
                else:
                    categoria_puesto = "Desarrollador Full Stack"  # Default
            
            # Conocimiento específico del puesto para evaluación contextual
            conocimiento_puesto = recommendation_generator.conocimiento_puesto.get(categoria_puesto, {})
            
            # Análisis detallado de lo que ya está presente en el CV
            elementos_presentes = {
                "perfil": {
                    "existe": bool(re.search(r'(perfil|resumen|objetivo|sobre\s+mí|presentación|summary|about)', texto_lower)),
                    "longitud_adecuada": len(re.findall(r'\b\w+\b', texto_lower[:500])) >= 30,
                    "menciona_puesto": puesto.lower() in texto_lower[:500],
                    "tiene_fortalezas": bool(re.search(r'(especializ|expert|habilidad|competen|conocimiento|experiencia|formación)', texto_lower[:500]))
                },
                "educacion": {
                    "existe": bool(re.search(r'(universidad|instituto|college|escuela|school|formación|education)', texto_lower)),
                    "tiene_fechas": bool(re.search(r'(19|20)\d\d\s*[-–]\s*((19|20)\d\d|presente|actualidad|actual)', texto_lower)) or bool(re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|sept|oct|nov|dic).{0,20}(19|20)\d\d', texto_lower)),
                    "tiene_titulacion": bool(re.search(r'(licenciatura|grado|ingeniería|bachiller|bachelor|engineering|título|maestría|máster|master|doctorado)', texto_lower)),
                    "tiene_cursos": bool(re.search(r'(curso|materia|asignatura|especialización|course|subject)', texto_lower))
                },
                "experiencia": {
                    "existe": bool(re.search(r'(experiencia|laboral|profesional|proyecto|trabajo|empleo|experience|work|job)', texto_lower)),
                    "tiene_fechas": bool(re.search(r'(19|20)\d\d\s*[-–]\s*((19|20)\d\d|presente|actualidad|actual)', texto_lower)) or bool(re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|sept|oct|nov|dic).{0,20}(19|20)\d\d', texto_lower)),
                    "tiene_empresas": bool(re.search(r'(empresa|compañía|organización|institución|company|organization)', texto_lower)),
                    "tiene_logros": bool(re.search(r'(logr|mejor|reduc|aument|implementa|desarrolla|optimiza|lidera)', texto_lower)),
                    "tiene_metricas": bool(re.search(r'\d+%|\d+\s+años|\d+\s+proyectos', texto_lower))
                },
                "habilidades": {
                    "existe": bool(re.search(r'(habilidad|competencia|conocimiento|técnica|skill|technology|stack|lenguajes|herramientas)', texto_lower)),
                    "organizadas": bool(re.search(r'(lenguajes|frameworks|herramientas|bases\s+de\s+datos|front|back)', texto_lower)),
                    "relevantes_puesto": False,  # Se evaluará abajo
                    "nivel_detallado": bool(re.search(r'(básico|intermedio|avanzado|experto|beginner|intermediate|advanced|expert)', texto_lower))
                },
                "certificados": {
                    "existe": bool(re.search(r'(certificado|certificación|diploma|acreditación|curso|formación|certification|course)', texto_lower)),
                    "tiene_fechas": bool(re.search(r'(certificado|certificación|diploma|curso).{0,50}(19|20)\d\d', texto_lower)),
                    "relevantes_puesto": False,  # Se evaluará abajo
                    "tiene_emisor": bool(re.search(r'(por|emitido|expedido|otorgado|issued|by)', texto_lower))
                },
                "idiomas": {
                    "existe": bool(re.search(r'(idioma|lenguaje|language)', texto_lower)),
                    "menciona_ingles": bool(re.search(r'(inglés|english)', texto_lower)),
                    "nivel_detallado": bool(re.search(r'(A1|A2|B1|B2|C1|C2|básico|intermedio|avanzado|nativo|fluido|beginner|intermediate|advanced|fluent|native)', texto_lower)) or bool(re.search(r'(inglés|english).{0,20}(b1|b2|c1|c2|intermedio|avanzado)', texto_lower)),
                    "tiene_certificaciones": bool(re.search(r'(TOEFL|IELTS|Cambridge|DELE|DALF|Goethe)', texto_lower))
                },
                "datos": {
                    "tiene_email": bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto_cv)),
                    "tiene_telefono": bool(re.search(r'(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}', texto_cv)),
                    "tiene_linkedin": bool(re.search(r'linkedin\.com\/in\/[a-zA-Z0-9_-]+', texto_lower)),
                    "tiene_github": bool(re.search(r'github\.com\/[a-zA-Z0-9_-]+', texto_lower)),
                    "tiene_web": bool(re.search(r'(website|sitio\s+web|portfolio|portafolio|blog)', texto_lower))
                },
                "formato": {
                    "tiene_secciones": bool(re.search(r'\n[A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]+\n', texto_cv)),
                    "tiene_viñetas": max(texto_cv.count('- '), texto_cv.count('• '), texto_cv.count('* ')) > 3,
                    "espaciado_adecuado": texto_cv.count('\n\n') >= 4,
                    "longitud_adecuada": 300 <= len(re.findall(r'\b\w+\b', texto_cv)) <= 1500
                }
            }
            
            # Evaluar relevancia de habilidades y certificaciones para el puesto
            tech_relevantes = conocimiento_puesto.get("tecnologías_clave", [])
            habilidades_relevantes = conocimiento_puesto.get("habilidades_técnicas", [])
            certificaciones_relevantes = conocimiento_puesto.get("certificaciones_valoradas", [])
            
            # Contar tecnologías y habilidades relevantes presentes (corregido)
            tech_encontradas = sum(1 for tech in tech_relevantes if tech.lower() in texto_lower)
            skills_encontradas = sum(1 for skill in habilidades_relevantes if any(word in texto_lower for word in skill.lower().split()))
            
            # Establecer si las habilidades son relevantes para el puesto
            elementos_presentes["habilidades"]["relevantes_puesto"] = (tech_encontradas >= len(tech_relevantes) * 0.3) or (skills_encontradas >= len(habilidades_relevantes) * 0.3) if tech_relevantes and habilidades_relevantes else True
            
            # Evaluar certificaciones relevantes (corregido)
            cert_encontradas = sum(1 for cert in certificaciones_relevantes if any(word in texto_lower for word in cert.lower().split() if len(word) > 3))
            elementos_presentes["certificados"]["relevantes_puesto"] = cert_encontradas > 0 if certificaciones_relevantes else True
            
            # Generar recomendaciones basadas en el análisis anterior
            recomendaciones = []
            
            # 1. Recomendaciones de Perfil
            if not elementos_presentes["perfil"]["existe"]:
                recomendaciones.append(f"Añade un perfil profesional al inicio del CV que resuma en 3-5 líneas tu experiencia y fortalezas clave para el puesto de {puesto}.")
            elif not elementos_presentes["perfil"]["longitud_adecuada"]:
                recomendaciones.append(f"Amplía tu perfil profesional para incluir más detalles sobre tu experiencia y habilidades relevantes para el puesto de {puesto}.")
            elif not elementos_presentes["perfil"]["menciona_puesto"] and not elementos_presentes["perfil"]["tiene_fortalezas"]:
                recomendaciones.append(f"Personaliza tu perfil para el puesto de {puesto}, destacando específicamente tus fortalezas y experiencia más relevantes para esta posición.")
            
            # 2. Recomendaciones de Educación
            if not elementos_presentes["educacion"]["existe"]:
                recomendaciones.append("Incluye tu formación académica con detalles de instituciones, titulaciones y fechas.")
            elif not elementos_presentes["educacion"]["tiene_fechas"]:
                recomendaciones.append("Añade fechas específicas (inicio-fin) a tu formación académica para mostrar tu trayectoria educativa.")
            elif not elementos_presentes["educacion"]["tiene_cursos"] and not "junior" in puesto.lower():
                recomendaciones.append(f"Complementa tu educación con cursos o especializaciones relacionadas con {puesto} para mostrar tu aprendizaje continuo.")
            
            # 3. Recomendaciones de Experiencia
            if not elementos_presentes["experiencia"]["existe"]:
                recomendaciones.append(f"Añade una sección de experiencia profesional o proyectos relacionados con {puesto}, incluso si son académicos o personales.")
            elif not elementos_presentes["experiencia"]["tiene_fechas"]:
                recomendaciones.append("Especifica las fechas (mes/año) de inicio y fin de cada experiencia profesional.")
            elif not elementos_presentes["experiencia"]["tiene_logros"]:
                recomendaciones.append("Enfoca tu experiencia en logros concretos, no solo en responsabilidades. Describe qué conseguiste en cada posición.")
            elif not elementos_presentes["experiencia"]["tiene_metricas"]:
                recomendaciones.append("Cuantifica tus logros con métricas específicas (%, tiempos, cantidades) para demostrar el impacto de tu trabajo.")
            
            # 4. Recomendaciones de Habilidades
            if not elementos_presentes["habilidades"]["existe"]:
                tech_ejemplo = ", ".join(tech_relevantes[:3]) if tech_relevantes else "tecnologías relevantes"
                recomendaciones.append(f"Añade una sección de habilidades técnicas que incluya {tech_ejemplo} y otras competencias relevantes para {puesto}.")
            elif not elementos_presentes["habilidades"]["organizadas"]:
                recomendaciones.append("Organiza tus habilidades por categorías (lenguajes, frameworks, herramientas, etc.) para mejorar la legibilidad.")
            elif not elementos_presentes["habilidades"]["relevantes_puesto"]:
                tech_faltantes = [tech for tech in tech_relevantes[:5] if tech.lower() not in texto_lower]
                if tech_faltantes:
                    tech_recomendadas = ", ".join(tech_faltantes[:3])
                    recomendaciones.append(f"Considera incluir o destacar tecnologías clave como {tech_recomendadas} que son altamente valoradas para el puesto de {puesto}.")
            
            # 5. Recomendaciones de Certificados
            if not elementos_presentes["certificados"]["existe"] and not "junior" in puesto.lower():
                cert_ejemplo = certificaciones_relevantes[0] if certificaciones_relevantes else "certificaciones relevantes"
                recomendaciones.append(f"Añade certificaciones profesionales como {cert_ejemplo} para validar tus conocimientos técnicos.")
            elif elementos_presentes["certificados"]["existe"] and not elementos_presentes["certificados"]["relevantes_puesto"]:
                cert_recomendadas = certificaciones_relevantes[0] if certificaciones_relevantes else "certificaciones específicas del área"
                recomendaciones.append(f"Considera obtener certificaciones más específicas como {cert_recomendadas} que son altamente valoradas para {puesto}.")
            
            # 6. Recomendaciones de Idiomas
            if not elementos_presentes["idiomas"]["existe"]:
                recomendaciones.append("Añade una sección de idiomas especificando tu nivel en cada uno, especialmente el inglés que es esencial en el sector tecnológico.")
            elif not elementos_presentes["idiomas"]["menciona_ingles"]:
                recomendaciones.append("Incluye tu nivel de inglés, ya que es fundamental para roles técnicos y el acceso a documentación actualizada.")
            elif elementos_presentes["idiomas"]["menciona_ingles"] and not elementos_presentes["idiomas"]["nivel_detallado"]:
                recomendaciones.append("Especifica tu nivel de inglés utilizando estándares reconocidos (A1-C2 o Básico/Intermedio/Avanzado/Nativo).")
            
            # 7. Recomendaciones de Datos de Contacto
            contactos_faltantes = []
            if not elementos_presentes["datos"]["tiene_email"]:
                contactos_faltantes.append("email profesional")
            if not elementos_presentes["datos"]["tiene_telefono"]:
                contactos_faltantes.append("teléfono")
            if not elementos_presentes["datos"]["tiene_linkedin"]:
                contactos_faltantes.append("perfil de LinkedIn")
            if not elementos_presentes["datos"]["tiene_github"] and ("desarrollador" in puesto.lower() or "programador" in puesto.lower() or "ingeniero" in puesto.lower()):
                contactos_faltantes.append("perfil de GitHub")
                
            if contactos_faltantes:
                recomendaciones.append(f"Incluye información de contacto completa: {', '.join(contactos_faltantes)}.")
            
            # 8. Recomendaciones de Formato
            if not elementos_presentes["formato"]["tiene_secciones"]:
                recomendaciones.append("Organiza tu CV en secciones claramente definidas con títulos destacados para facilitar la lectura.")
            elif not elementos_presentes["formato"]["tiene_viñetas"]:
                recomendaciones.append("Utiliza viñetas para presentar tu experiencia, logros y habilidades de forma más escanenable y organizada.")
            elif not elementos_presentes["formato"]["espaciado_adecuado"]:
                recomendaciones.append("Mejora el espaciado y la estructura visual del CV para facilitar su lectura y hacerlo más profesional.")
            elif not elementos_presentes["formato"]["longitud_adecuada"]:
                recomendaciones.append("Ajusta la longitud de tu CV a 1-2 páginas, priorizando la información más relevante para el puesto.")
            
            # Añadir recomendaciones específicas según el puesto
            if tendencias := conocimiento_puesto.get("tendencias_2025", []):
                if not any(tendencia.lower() in texto_lower for tendencia in tendencias[:3]):
                    tendencia_recomendada = tendencias[0] if tendencias else "tendencias actuales del sector"
                    recomendaciones.append(f"Considera mencionar experiencia o interés en {tendencia_recomendada}, una tendencia clave para profesionales de {puesto} en 2025.")
            
            # Limitar a las recomendaciones más importantes y diversas
            recomendaciones = list(dict.fromkeys(recomendaciones))  # Eliminar duplicados manteniendo orden
            
            # Si hay demasiadas recomendaciones, priorizarlas
            if len(recomendaciones) > 7:
                # Priorizar recomendaciones de distintas secciones
                secciones_cubiertas = set()
                recomendaciones_priorizadas = []
                
                for recomendacion in recomendaciones:
                    seccion = None
                    if "perfil" in recomendacion.lower():
                        seccion = "perfil"
                    elif "educación" in recomendacion.lower() or "formación" in recomendacion.lower():
                        seccion = "educacion"
                    elif "experiencia" in recomendacion.lower():
                        seccion = "experiencia"
                    elif "habilidades" in recomendacion.lower() or "tecnologías" in recomendacion.lower():
                        seccion = "habilidades"
                    elif "certificaciones" in recomendacion.lower():
                        seccion = "certificados"
                    elif "idiomas" in recomendacion.lower() or "inglés" in recomendacion.lower():
                        seccion = "idiomas"
                    elif "contacto" in recomendacion.lower():
                        seccion = "datos"
                    elif "organiza" in recomendacion.lower() or "estructura" in recomendacion.lower() or "formato" in recomendacion.lower():
                        seccion = "formato"
                    
                    if seccion and seccion not in secciones_cubiertas:
                        recomendaciones_priorizadas.append(recomendacion)
                        secciones_cubiertas.add(seccion)
                        
                    if len(recomendaciones_priorizadas) >= 7:
                        break
                        
                # Si no se llegó a 7, añadir el resto
                if len(recomendaciones_priorizadas) < 7:
                    for recomendacion in recomendaciones:
                        if recomendacion not in recomendaciones_priorizadas:
                            recomendaciones_priorizadas.append(recomendacion)
                            if len(recomendaciones_priorizadas) >= 7:
                                break
                                
                recomendaciones = recomendaciones_priorizadas
            
            # Asegurar un mínimo de 4 recomendaciones
            if len(recomendaciones) < 4:
                recomendaciones_genericas = [
                    f"Personaliza mejor tu perfil profesional para el puesto de {puesto}, destacando tus fortalezas clave.",
                    "Cuantifica tus logros con métricas específicas (%, números, tiempos) para demostrar impacto.",
                    "Organiza tus habilidades técnicas por categorías para mejorar la legibilidad y relevancia.",
                    "Mejora el formato visual con viñetas, espaciado y estructura consistente."
                ]
                
                # Añadir recomendaciones genéricas que no estén ya incluidas
                for rec in recomendaciones_genericas:
                    if not any(r.lower() in rec.lower() or rec.lower() in r.lower() for r in recomendaciones):
                        recomendaciones.append(rec)
                        if len(recomendaciones) >= 4:
                            break
            
            # Limitar a exactamente 7 recomendaciones máximo
            return recomendaciones[:8]
            
        except Exception as e:
            print(f"Error generando recomendaciones: {str(e)}")
            # Recomendaciones genéricas de respaldo en caso de error
            return [
                f"Personaliza tu perfil para el puesto de {puesto}, destacando tu experiencia relevante.",
                "Cuantifica tus logros profesionales con métricas específicas (%, números, resultados).",
                f"Destaca las habilidades técnicas más valoradas para {puesto}.",
                "Organiza tu CV en secciones claras con viñetas para facilitar la lectura.",
                "Incluye información de contacto completa y perfiles profesionales online.",
                "Ajusta la longitud del CV a máximo 2 páginas, priorizando la información relevante.",
                "Especifica tu nivel de inglés, esencial para roles técnicos."
            ]
        
    

# === Inicializar el generador de recomendaciones ===
recommendation_generator = CVRecommendationGenerator()
print("✅ Generador de recomendaciones inicializado")

# === Cargar modelo BERT ===
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    print("✅ Modelo BERT cargado exitosamente")
except Exception as e:
    print(f"❌ Error cargando modelo BERT: {str(e)}")
    tokenizer, model = None, None

# === Utilidades de texto ===
def extraer_texto_pdf(ruta: str) -> str:
    try:
        with fitz.open(ruta) as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        raise Exception(f"Error leyendo PDF: {str(e)}")

def extraer_texto_docx(ruta: str) -> str:
    try:
        if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
            raise Exception("Archivo DOCX no encontrado o vacío")
        doc = Document(ruta)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except Exception as e:
        raise Exception(f"Error leyendo DOCX: {str(e)}")

async def procesar_archivo(archivo: UploadFile) -> str:
    try:
        temp_dir = Path(tempfile.mkdtemp())
        temp_file_path = temp_dir / archivo.filename
        content = await archivo.read()
        if not content:
            raise Exception("Archivo vacío")
        with open(temp_file_path, "wb") as f:
            f.write(content)
        if archivo.filename.lower().endswith('.pdf'):
            texto = extraer_texto_pdf(str(temp_file_path))
        else:
            texto = extraer_texto_docx(str(temp_file_path))
        return texto
    except Exception as e:
        raise Exception(f"Error procesando archivo: {str(e)}")
    finally:
        try:
            if 'temp_file_path' in locals() and temp_file_path.exists():
                temp_file_path.unlink()
            if 'temp_dir' in locals() and temp_dir.exists():
                temp_dir.rmdir()
        except Exception as e:
            print(f"Error limpiando archivos temporales: {str(e)}")

def obtener_embedding(texto: str) -> torch.Tensor:
    if not tokenizer or not model:
        raise Exception("Modelo BERT no disponible")
    
    # Truncar texto si es necesario para evitar errores de memoria
    max_tokens = 512
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, max_length=max_tokens)
    
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :]

# === Generación de recomendaciones sin APIs externas ===
async def generar_recomendaciones(puesto: str, cv_texto: str) -> list:
    """
    Genera recomendaciones para mejorar el CV sin usar APIs externas
    
    Args:
        puesto: Puesto al que aplica el usuario
        cv_texto: Texto extraído del CV
        
    Returns:
        Lista de recomendaciones para mejorar el CV
    """
    try:
        print("🔄 Generando recomendaciones con sistema local...")
        # Usa el generador para obtener recomendaciones personalizadas
        recomendaciones = recommendation_generator.generar_recomendaciones(cv_texto, puesto)
        print(f"✅ Recomendaciones generadas: {len(recomendaciones)} items")
        return recomendaciones
    except Exception as e:
        print(f"⚠️ Error en generador de recomendaciones: {str(e)}")
        # Función de respaldo con recomendaciones genéricas
        return generar_recomendaciones_offline(puesto, cv_texto)

# Función de respaldo por si acaso
def generar_recomendaciones_offline(puesto: str, cv_texto: str) -> list:
    """Genera recomendaciones básicas cuando el sistema principal no está disponible"""
    print("🔄 Usando generador de recomendaciones offline (respaldo)")
    
    # Determinar área del puesto
    area_puesto = ""
    if "desarrollador" in puesto.lower() or "programador" in puesto.lower() or "frontend" in puesto.lower() or "fullstack" in puesto.lower():
        area_puesto = "desarrollo de software"
        keywords = ["proyectos de código", "GitHub", "lenguajes de programación", "frameworks", "metodologías ágiles"]
    elif "datos" in puesto.lower() or "data" in puesto.lower() or "big data" in puesto.lower():
        area_puesto = "análisis de datos"
        keywords = ["proyectos analíticos", "herramientas de datos", "algoritmos", "visualización", "estadística"]
    elif "cloud" in puesto.lower() or "devops" in puesto.lower() or "sre" in puesto.lower():
        area_puesto = "infraestructura cloud"
        keywords = ["soluciones cloud", "automatización", "CI/CD", "IaC", "containerización"]
    elif "seguridad" in puesto.lower() or "security" in puesto.lower() or "ciber" in puesto.lower():
        area_puesto = "ciberseguridad"
        keywords = ["protocolos de seguridad", "herramientas de protección", "análisis de riesgos", "ethical hacking", "compliance"]
    elif "arquitecto" in puesto.lower():
        area_puesto = "arquitectura de sistemas"
        keywords = ["diseños arquitectónicos", "patrones", "escalabilidad", "sistemas distribuidos", "diagramas"]
    elif "ia" in puesto.lower() or "ml" in puesto.lower() or "machine learning" in puesto.lower():
        area_puesto = "inteligencia artificial"
        keywords = ["modelos", "datasets", "algoritmos", "deep learning", "frameworks de IA"]
    else:
        area_puesto = "tecnología"
        keywords = ["proyectos técnicos", "herramientas especializadas", "metodologías", "innovaciones", "soluciones"]
    
    # Lista de recomendaciones genéricas pero adaptadas al puesto
    recomendaciones = [
        f"Destaca tu experiencia con {keywords[0]} recientes relacionados específicamente con {area_puesto}, detallando tu rol y contribuciones concretas en cada uno.",
        
        f"Incluye enlaces a tu portafolio o repositorios de código que demuestren tu experiencia práctica en {area_puesto}, particularmente con ejemplos relevantes para el puesto de {puesto}.",
        
        f"Enumera claramente los {keywords[1]} que dominas, especificando tu nivel de competencia en cada uno y priorizando los más relevantes para el puesto de {puesto}.",
        
        f"Cuantifica tus logros profesionales con métricas específicas (porcentajes, tiempos, KPIs) que demuestren el impacto de tu trabajo en {area_puesto}.",
        
        f"Personaliza la sección de habilidades técnicas específicamente para el puesto de {puesto}, destacando tu dominio de {keywords[2]} y otras competencias fundamentales para este rol.",
        
        f"Mejora las descripciones de tu experiencia con ejemplos específicos de aplicación de {keywords[3]} en entornos reales, demostrando tu capacidad para resolver problemas complejos.",
        
        f"Complementa tu formación académica con certificaciones, cursos especializados o proyectos de auto-aprendizaje relacionados con {keywords[4]} y otras áreas clave para el puesto de {puesto}."
    ]
    
    return recomendaciones


# === Evaluación CV ===
async def evaluar_cv(texto_cv: str, puesto: str = "") -> tuple:
    """
    Evalúa un CV con detalles específicos sobre cada sección
    
    Args:
        texto_cv: Texto extraído del CV
        puesto: Puesto al que aplica el usuario
        
    Returns:
        Tupla con: (puntaje_total, lista_de_detalles_por_seccion)
    """
    # Preprocesamiento del texto para normalizar formatos
    texto_cv = re.sub(r'[•●■◆▪▫☐☑✓✔]\s', '• ', texto_cv)
    texto_cv = texto_cv.replace('–', '-').replace('—', '-')
    texto_cv = re.sub(r'\s+', ' ', texto_cv) 
    

    # Criterios de evaluación con mensajes detallados de retroalimentación
    secciones = {
        "Perfil": {
            "keywords": ["perfil", "presentación", "objetivo", "resumen", "sobre mí", "summary", "about me"],
            "max_puntos": 15,
            "criterios": {
                "presencia": "Se encontró sección de perfil profesional",
                "longitud": "El perfil tiene longitud adecuada (50-150 palabras)",
                "relevancia": f"El perfil está orientado al puesto de {puesto}",
                "claridad": "El perfil comunica claramente tus capacidades y objetivos",
                "enfoque": "El perfil destaca tus principales fortalezas para el puesto"
            },
            "mensaje_excelente": f"Excelente resumen profesional que comunica claramente tu valor para el puesto de {puesto}. Incluye tus fortalezas clave y experiencia más relevante.",
            "mensaje_bueno": f"Buen perfil profesional que menciona tus capacidades para el puesto de {puesto}. Podría ser aún más específico sobre tus logros destacados.",
            "mensaje_regular": f"Tu perfil es básico pero funcional. Considera personalizarlo más específicamente para el puesto de {puesto}, destacando habilidades relevantes.",
            "mensaje_mejorable": "Te falta una sección de perfil profesional sólida. Añade un resumen al inicio del CV que presente tus principales fortalezas y tu propuesta de valor única."
        },
        "Educación": {
            "keywords": ["universidad", "carrera", "estudios", "licenciatura", "máster", "formación", "education", "degree"],
            "max_puntos": 15,
            "criterios": {
                "presencia": "Se encontró sección de educación",
                "detalle": "Incluye nombre de instituciones y títulos completos",
                "fechas": "Especifica fechas de inicio y fin (o fecha esperada de graduación)",
                "relevancia": f"La formación es relevante para el puesto de {puesto}",
                "organización": "La información está bien estructurada y fácil de leer"
            },
            "mensaje_excelente": "Excelente detalle en tu formación académica, incluyendo titulaciones, instituciones, fechas y logros relevantes durante tus estudios.",
            "mensaje_bueno": "Buena sección de educación con información clara sobre tus titulaciones. Considera añadir proyectos académicos relevantes.",
            "mensaje_regular": "Sección de educación básica pero incompleta. Añade más detalles sobre tus estudios, especialmente proyectos o cursos relevantes.",
            "mensaje_mejorable": "Falta información detallada sobre tu formación académica. Incluye instituciones, titulaciones completas, fechas y especialización relevante."
        },
        "Habilidades": {
            "keywords": ["habilidad", "tecnología", "herramienta", "competencia", "conocimiento", "skills", "technologies"],
            "max_puntos": 15,
            "criterios": {
                "presencia": "Se encontró sección de habilidades técnicas",
                "relevancia": f"Las habilidades son relevantes para el puesto de {puesto}",
                "organización": "Las habilidades están organizadas por categorías",
                "nivel": "Se especifica el nivel de dominio en cada habilidad",
                "actualización": "Incluye tecnologías y herramientas actuales"
            },
            "mensaje_excelente": f"Excelente sección de habilidades, bien organizada y con tecnologías perfectamente alineadas con el puesto de {puesto}. Incluye nivel de competencia y herramientas actuales.",
            "mensaje_bueno": f"Buena sección de habilidades técnicas relevantes para {puesto}. Considera organizarlas por categorías y especificar tu nivel en cada una.",
            "mensaje_regular": "Tus habilidades están listadas pero podrían estar mejor organizadas y priorizadas según su relevancia para el puesto.",
            "mensaje_mejorable": f"Falta una sección clara de habilidades técnicas. Añade una lista organizada de tecnologías y competencias relevantes para {puesto}."
        },
        "Experiencia": {
            "keywords": ["experiencia", "proyecto", "trabajo", "empleo", "profesional", "experience", "work"],
            "max_puntos": 15,
            "criterios": {
                "presencia": "Se encontró sección de experiencia profesional",
                "estructura": "Cada experiencia incluye empresa, cargo, fechas y responsabilidades",
                "logros": "Menciona logros cuantificables, no solo responsabilidades",
                "relevancia": f"Las experiencias son relevantes para el puesto de {puesto}",
                "cronología": "Presenta experiencias en orden cronológico inverso (más reciente primero)"
            },
            "mensaje_excelente": f"Excelente detalle en tu experiencia profesional con logros cuantificables claramente vinculados al puesto de {puesto}. Buena estructura con contexto, responsabilidades y resultados.",
            "mensaje_bueno": f"Buena sección de experiencia con roles claramente descritos. Para mejorar, añade más logros cuantificables y alinea mejor con las responsabilidades de {puesto}.",
            "mensaje_regular": "Tu experiencia está descrita de manera básica. Mejora añadiendo métricas y resultados concretos en lugar de solo listar responsabilidades.",
            "mensaje_mejorable": f"Falta detallar mejor tu experiencia. Estructura cada posición con: cargo, empresa, fechas, responsabilidades clave y resultados cuantificables relevantes para {puesto}."
        },
        "Certificados": {
            "keywords": ["certificado", "curso", "capacitación", "diplomado", "certification", "course"],
            "max_puntos": 10,  # CORRECCIÓN 1: Ya estaba en 10 (no 15 como mencionaste)
            "criterios": {
                "presencia": "Se encontró sección de certificaciones o formación complementaria",
                "actualidad": "Incluye certificaciones actuales y relevantes",
                "detalle": "Especifica institución emisora y fecha de obtención",
                "relevancia": f"Las certificaciones son valiosas para el puesto de {puesto}",
                "organización": "La información está bien presentada y priorizada"
            },
            "mensaje_excelente": f"Excelentes certificaciones, actualizadas y altamente relevantes para el puesto de {puesto}. Bien presentadas con fechas e instituciones emisoras.",
            "mensaje_bueno": f"Buenas certificaciones relacionadas con el puesto de {puesto}. Considera obtener certificaciones más especializadas o actuales.",
            "mensaje_regular": "Tienes algunas certificaciones listadas, pero podrían ser más relevantes o actuales para el puesto al que aplicas.",
            "mensaje_mejorable": f"Faltan certificaciones relevantes para validar tus conocimientos técnicos. Considera obtener y añadir certificaciones reconocidas en el campo de {puesto}."
        },
        "Idiomas": {
            "keywords": ["idioma", "inglés", "español", "nivel", "language", "fluent", "proficient", "native"],
            "max_puntos": 10,
            "criterios": {
                "presencia": "Se encontró sección de idiomas",
                "niveles": "Especifica nivel de dominio de cada idioma (A1-C2 o básico/intermedio/avanzado)",
                "inglés": "Menciona nivel de inglés (esencial en tecnología)",
                "detalle": "Incluye capacidades específicas (lectura, escritura, conversación)",
                "certificaciones": "Menciona certificaciones de idiomas si las tiene"
            },
            "mensaje_excelente": "Excelente detalle en tus competencias lingüísticas, especificando niveles según el Marco Común Europeo y áreas de dominio específicas.",
            "mensaje_bueno": "Buena sección de idiomas con niveles de competencia. Considera añadir certificaciones o contextos de uso técnico.",
            "mensaje_regular": "Mencionas tus idiomas pero con poco detalle. Especifica mejor tu nivel en cada uno, especialmente tu dominio del inglés técnico.",
            "mensaje_mejorable": "Falta una sección clara de idiomas. Añade tus competencias lingüísticas especificando tu nivel en cada idioma, especialmente en inglés."
        },
        "Datos": {
            "keywords": ["contacto", "email", "teléfono", "linkedin", "github", "contact", "phone", "website", "portfolio"],
            "max_puntos": 10,
            "criterios": {
                "presencia": "Se encontró información de contacto",
                "email": "Incluye email profesional",
                "teléfono": "Incluye número de teléfono de contacto",
                "redes": "Incluye perfiles profesionales (LinkedIn, GitHub, etc.)",
                "presentación": "La información está bien destacada y accesible"
            },
            "mensaje_excelente": "Excelente información de contacto, completa y bien organizada, incluyendo email, teléfono y perfiles profesionales relevantes como LinkedIn y GitHub.",
            "mensaje_bueno": "Buena información de contacto con datos esenciales. Considera añadir enlaces a perfiles profesionales o portafolio.",
            "mensaje_regular": "Información de contacto básica pero incompleta. Añade más canales para que los reclutadores puedan contactarte.",
            "mensaje_mejorable": "Falta información de contacto completa y destacada. Asegúrate de incluir email profesional, teléfono y enlaces a tus perfiles en plataformas relevantes."
        },
        "Formato": {
            "keywords": [],
            "max_puntos": 10,  # CORRECCIÓN 1: Aumentado de 5 a 10 para llegar a un total de 100
            "criterios": {
                "longitud": "CV con longitud adecuada (1-2 páginas)",
                "organización": "Información bien estructurada y fácil de escanear",
                "consistencia": "Formato consistente en títulos, viñetas y espaciado",
                "legibilidad": "Texto legible con uso adecuado de negritas y énfasis",
                "priorización": "Información más relevante destacada y priorizada"
            },
            "mensaje_excelente": "Excelente formato, perfectamente estructurado, conciso y fácil de escanear. Prioriza adecuadamente la información más relevante.",
            "mensaje_bueno": "Buen formato general con estructura clara. Algunos pequeños ajustes de espaciado o consistencia mejorarían la legibilidad.",
            "mensaje_regular": "Formato aceptable pero mejorable. Trabaja en la consistencia visual y en facilitar la lectura rápida de la información clave.",
            "mensaje_mejorable": "El formato necesita mejoras significativas. Estructura mejor la información, usa viñetas, espaciado consistente y destaca la información importante."
        }
    }
    
    resultados = []
    puntaje_total = 0
    texto_lower = texto_cv.lower()
    
    # Identificar categoría de puesto para evaluación más específica
    categoria_puesto = None
    for key in recommendation_generator.conocimiento_puesto.keys():
        if key.lower() in puesto.lower() or puesto.lower() in key.lower():
            categoria_puesto = key
            break
    
    # Si no hay match, usar una categoría por defecto
    if not categoria_puesto:
        if "desarrollador" in puesto.lower() or "programador" in puesto.lower():
            categoria_puesto = "Desarrollador Full Stack"
        elif "datos" in puesto.lower() or "data" in puesto.lower():
            categoria_puesto = "Ingeniero de Datos"
        else:
            categoria_puesto = "Desarrollador Full Stack"  # Default
    
    # Conocimiento específico del puesto para evaluación contextual
    conocimiento_puesto = recommendation_generator.conocimiento_puesto.get(categoria_puesto, {})
    

    # Pre-análisis para identificar características globales del CV
    es_pdf = "\uf0b7" in texto_cv or len(re.findall(r'[^\x00-\x7F]', texto_cv)) > 5
    tiene_emojis = len(re.findall(r'[\U0001F300-\U0001F6FF]', texto_cv)) > 0
    primeras_lineas = "\n".join(texto_cv.split("\n")[:15])
    
    # Detectar tecnologías relevantes en todo el CV para análisis global
    tech_relevantes = conocimiento_puesto.get("tecnologías_clave", [])
    habilidades_relevantes = conocimiento_puesto.get("habilidades_técnicas", [])
    
    tech_count_global = sum(1 for tech in tech_relevantes if re.search(rf'\b{re.escape(tech.lower())}\b', texto_lower))
    skills_count_global = sum(1 for skill in habilidades_relevantes if any(re.search(rf'\b{re.escape(word)}\b', texto_lower) for word in skill.lower().split()))
    
    # Factor de calidad técnica global (0.0-1.0) que influirá en ajustes finales
    factor_tecnico = 0.0
    if tech_relevantes and habilidades_relevantes:
        factor_tech = min(1.0, tech_count_global / (len(tech_relevantes) * 0.7))
        factor_skills = min(1.0, skills_count_global / (len(habilidades_relevantes) * 0.7))
        factor_tecnico = (factor_tech * 0.6) + (factor_skills * 0.4)



    for seccion, datos in secciones.items():
        keywords = datos["keywords"]
        max_puntos = datos["max_puntos"]
        criterios = datos["criterios"]
        
        # Evaluación por criterios
        # Evaluación de formato mejorada
        if not keywords:  # Sección de Formato
            lineas = texto_cv.split('\n')
            palabras = len(re.findall(r'\b\w+\b', texto_cv))
            parrafos = [p for p in texto_cv.split('\n\n') if p.strip()]
            
            criterios_cumplidos = 0
            
            # 1. Longitud adecuada (1-2 páginas)
            if 300 <= palabras <= 2500:  # Rango ampliado
                criterios_cumplidos += 1
            
            # 2. Estructura clara (buscar diferentes tipos de delimitadores de sección)
            secciones_detectadas = len(re.findall(r'\n##?\s+[A-Z][A-Za-z\s]+', texto_cv))
            secciones_alt = len(re.findall(r'\n[A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]+:?\s*\n', texto_cv))
            secciones_emoji = len(re.findall(r'[\U0001F300-\U0001F6FF][\s\w]+:', texto_cv))
            
            if secciones_detectadas >= 3 or secciones_alt >= 3 or secciones_emoji >= 3:
                criterios_cumplidos += 1
            
            # 3. Consistencia visual (buscar patrones de estructuración)

            tiene_formato_moderno = False

            if tiene_emojis:
                criterios_cumplidos += 1
                tiene_formato_moderno = True

            if (re.search(r'^[A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]+:?\s*$', texto_cv, re.MULTILINE) or
                re.search(r'^[A-ZÑÁÉÍÓÚ][A-ZÑÁÉÍÓÚa-zñáéíóú\s]+\n[-=_]{3,}', texto_cv, re.MULTILINE)):
                criterios_cumplidos += 1
            
            # 4. Uso de viñetas (buscar diferentes tipos de viñetas)
            # 4.1 Buscar varios tipos de viñetas con un umbral más bajo
            viñetas = sum(texto_cv.count(v) for v in ['- ', '• ', '* ', '○ ', '▪ ', '◦ ', '· '])
            if viñetas >= 3:  # Reducir el umbral a 3
                criterios_cumplidos += 1
            
            # 4.2 Buscar patrones de lista numérica (también válidos)
            num_items = len(re.findall(r'^\d+\.\s+', texto_cv, re.MULTILINE))
            if num_items >= 3:
                criterios_cumplidos += 0.5
            
            # 5. Espaciado adecuado (entre secciones)
            if texto_cv.count('\n\n') >= 4:  # Al menos 4 separaciones de sección
                criterios_cumplidos += 0.5
            
            # 5.2 Información priorizada (info clave al inicio)
            if re.search(r'(nombre|name)|(email|correo)|(teléfono|phone)|linkedin|github', primeras_lineas.lower()):
                criterios_cumplidos += 0.5

            # 6. Detección de información clave
            info_clave = sum(1 for _ in re.finditer(
                r'(email|tel[ée]fono|linkedin|github|http[s]?://)', 
                texto_cv, re.IGNORECASE))
            if info_clave >= 3:
                criterios_cumplidos += 0.5
            

            # 7. Detección de formato PDF (compensar por pérdida de formato en extracción)
            if es_pdf:
                # Los PDFs pueden perder formato en la extracción pero generalmente tienen buen diseño
                criterios_cumplidos += 0.5
                # Si además muestra evidencia de contenido técnico sólido
                if factor_tecnico > 0.6:
                    criterios_cumplidos += 0.5
            
            # Normalización y cálculo final de puntos
            criterios_cumplidos = min(10, criterios_cumplidos)  # CORRECCIÓN 1: Máximo 10 criterios en vez de 5
            
            # Puntuación base según criterios cumplidos
            puntos = (criterios_cumplidos / 10) * max_puntos  # CORRECCIÓN 1: Dividir por 10 en vez de 5
            
            # Compensación para CVs altamente técnicos aunque con formato no estándar
            if factor_tecnico > 0.7 and puntos < 6:  # CORRECCIÓN 1: Ajustado de 3 a 6 por la escala de 10 puntos
                puntos = min(6, puntos + 2)  # CORRECCIÓN 1: Ajustado de 3 a 6, y de 1 a 2

            # CORRECCIÓN 2: Sistema de feedback más preciso
            # Sistema de feedback detallado
            feedback_messages = {
                10: "✅ Formato excelente: Estructura profesional y fácil de entender",
                9: "✅ Formato excelente: Estructura profesional y fácil de entender",
                8: "✅ Muy bueno: Formato profesional y claro",
                7: "✅ Bueno: Formato ordenado y legible",
                6: "⚠️ Aceptable: Podría mejorar en consistencia",
                5: "⚠️ Regular: Necesita ajustes de estructura",
                4: "⚠️ Regular: Algunos elementos necesitan mejora",
                3: "❌ Deficiente: Requiere revisión de estructura",
                2: "❌ Deficiente: Requiere revisión de estructura",
                1: "❌ Muy deficiente: Necesita restructuración completa",
                0: "❌ Ausente: No se detecta estructura formal"
            }
            
            feedback = feedback_messages.get(round(criterios_cumplidos), 
                    "⚠️ Regular: Algunos elementos necesitan mejora")
            
            # Asegurar puntaje dentro de rango
            puntos = min(max_puntos, max(1, round(puntos)))


        else:
            # CORRECCIÓN 3-4: Mejora en la evaluación de secciones, especialmente "Datos"
            if seccion == "Datos":
                # Análisis más estricto de la información de contacto
                # Reiniciar criterios cumplidos para esta sección específica
                criterios_cumplidos = 0
                criterios_total = 5  # Cinco criterios en total
                
                # 1. Email profesional (verificación más estricta)
                tiene_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto_cv))
                if tiene_email:
                    criterios_cumplidos += 1
                    # Verificar si el email está en un contexto adecuado (no solo aparece casualmente)
                    if re.search(r'(email|correo|e-mail|mail|contacto)[:;]?\s*[a-zA-Z0-9._%+-]+@', texto_lower):
                        criterios_cumplidos += 0.5
                
                # 2. Teléfono (verificación más estricta)
                patrones_telefono = [
                    r'(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}',
                    r'\d{2,3}[\s.-]?\d{2,3}[\s.-]?\d{2,3}[\s.-]?\d{2,3}',
                ]
                
                tiene_telefono = any(re.search(patron, texto_cv) for patron in patrones_telefono)
                if tiene_telefono:
                    # Verificar si el teléfono está en un contexto adecuado
                    if re.search(r'(teléfono|telefono|celular|móvil|tel|phone|contacto)[:;]?\s*(\+?\d|\(\d)', texto_lower):
                        criterios_cumplidos += 1
                    else:
                        # Si solo hay números sin contexto, otorgar menos puntos
                        criterios_cumplidos += 0.5
                
                # 3. Nombre completo (nuevo criterio importante)
                patrones_nombre = [
                    r'(nombre|name)[:;]?\s*[A-Z][a-zñáéíóú]+\s+[A-Z][a-zñáéíóú]+',
                    r'^[A-Z][a-zñáéíóú]+\s+[A-Z][a-zñáéíóú]+(\s+[A-Z][a-zñáéíóú]+)?',  # Al inicio del CV
                ]
                
                tiene_nombre_completo = any(re.search(patron, texto_cv) for patron in patrones_nombre)
                if tiene_nombre_completo:
                    criterios_cumplidos += 1
                # Verificar si al menos tiene algún nombre (no necesariamente completo)
                elif re.search(r'[A-Z][a-zñáéíóú]+\s+[A-Z][a-zñáéíóú]+', texto_cv):
                    criterios_cumplidos += 0.5
                
                # 4. Perfiles profesionales (LinkedIn, GitHub, etc.)
                patrones_perfiles = [
                    r'linkedin\.com\/in\/[a-zA-Z0-9_-]+',
                    r'github\.com\/[a-zA-Z0-9_-]+',
                    r'(linkedin|github|gitlab).{0,20}[a-zA-Z0-9_-]+'
                ]
                
                perfiles_encontrados = sum(1 for patron in patrones_perfiles if re.search(patron, texto_lower))
                if perfiles_encontrados >= 2:
                    criterios_cumplidos += 2
                elif perfiles_encontrados == 1:
                    criterios_cumplidos += 1
                
                # 5. Ubicación o ciudad (útil para reclutadores)
                if re.search(r'(ciudad|ubicación|location|dirección|address|city)[:;]?\s*[A-Z][a-zñáéíóú]+', texto_lower):
                    criterios_cumplidos += 0.5
                
                # Normalizar y calcular puntos
                criterios_cumplidos = min(criterios_total, criterios_cumplidos)
                puntos = (criterios_cumplidos / criterios_total) * max_puntos
                
                # Asegurar que no se dé puntuación perfecta a menos que cumpla estrictamente todos los criterios
                if puntos > max_puntos * 0.9 and (not tiene_email or not tiene_telefono or perfiles_encontrados < 1):
                    puntos = max_puntos * 0.8  # Máximo 80% si falta algún elemento esencial
                
                puntos = min(max_puntos, max(1, round(puntos)))

            else:

            
                # Análisis de presencia de keywords y criterios específicos
                presentes = sum(1 for kw in keywords if kw in texto_lower)
                
                # Criterios específicos por sección
                criterios_cumplidos = 0
                criterios_total = len(criterios)
                
                # Criterio básico: presencia de keywords
                if presentes > 0:
                    criterios_cumplidos += 1
                    
                # Criterios específicos por sección
                if seccion == "Perfil":
                    # DETECCIÓN MEJORADA DE PERFIL - ENFOQUE MULTIPERSPECTIVA
                    
                    # 1. Perfil explícito tradicional
                    patron_perfil = re.search(r'(perfil|resumen|objetivo|sobre\s+mí|presentación|summary|about).{10,}', texto_lower, re.DOTALL)
                    if patron_perfil:
                        contenido_perfil = patron_perfil.group(0)
                        
                        # Longitud adecuada
                        if 30 <= len(contenido_perfil.split()) <= 250:
                            criterios_cumplidos += 1
                        
                        # Mención de habilidades relevantes
                        if any(tech.lower() in contenido_perfil for tech in tech_relevantes) or any(re.search(rf'\b{re.escape(word)}\b', contenido_perfil) for skill in habilidades_relevantes for word in skill.lower().split()):
                            criterios_cumplidos += 1
                        
                        # Enfoque en resultados o valor
                        if re.search(r'(result|valor|impact|logr|contribu|especiali|expert|soluc|desarro|implement|diseñ)', contenido_perfil):
                            criterios_cumplidos += 1
                    
                    # 2. Perfil implícito moderna - Información clave al inicio
                    tiene_contacto_inicio = (
                        re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', primeras_lineas.lower()) or
                        re.search(r'(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}', primeras_lineas.lower()) or
                        re.search(r'linkedin\.com|github\.com', primeras_lineas.lower())
                    )
                    
                    # Nombre y rol/cargo al inicio (típico en CVs actuales)
                    tiene_rol_inicio = re.search(r'(ingenier[oa]|desarrollador[a]?|programador[a]?|analista|especialista|consultor|senior|ssr|full[\s-]?stack|front[\s-]?end|back[\s-]?end)', primeras_lineas.lower())
                    
                    if tiene_contacto_inicio:
                        criterios_cumplidos += 1
                        
                    if tiene_rol_inicio:
                        criterios_cumplidos += 1
                
                    # Si tiene tanto contacto como rol al inicio, considerar como perfil bien estructurado
                    if tiene_contacto_inicio and tiene_rol_inicio:
                        criterios_cumplidos += 1
                    
                    # 3. Tecnologías clave mencionadas en las primeras líneas (muestra enfoque)
                    tech_en_inicio = sum(1 for tech in tech_relevantes if tech.lower() in primeras_lineas.lower())
                    if tech_en_inicio >= 3:
                        criterios_cumplidos += 1
                    elif tech_en_inicio > 0:
                        criterios_cumplidos += 0.5
                    
                    # 4. Años de experiencia o nivel mencionado al inicio (común en perfiles profesionales)
                    if re.search(r'(\d+[\+]?\s*años|senior|ssr|jr|junior|mid\s*level|mid\s*senior|experiencia)', primeras_lineas.lower()):
                        criterios_cumplidos += 1
                    
                    # 5. Para PDFs, ser más flexibles con la detección de perfil
                    if es_pdf and criterios_cumplidos > 0 and criterios_cumplidos < 3:
                        criterios_cumplidos += 1  # Bonus para compensar extracción
                        
                elif seccion == "Experiencia":
                    # DETECCIÓN MEJORADA DE EXPERIENCIA
                    
                    # 1. Verificar logros cuantificables (con varios patrones)
                    patrones_logros = [
                        r'\d+%',  # Porcentajes
                        r'(reduc|reduj|disminuy|aument|increment|mejor|optimiz).{0,20}\d+',  # Mejoras cuantificadas
                        r'(implement|desarrolla|crea|diseñ).{0,30}(sistema|aplicación|proyecto|plataforma|solución)',  # Implementaciones
                        r'(lideri?c?e?|dirigi).{0,30}(equipo|proyecto|desarrollo|implementación)'  # Liderazgo
                    ]
                    
                    logros_encontrados = sum(1 for patron in patrones_logros if re.search(patron, texto_lower))
                    if logros_encontrados >= 2:
                        criterios_cumplidos += 2
                    elif logros_encontrados >= 1:
                        criterios_cumplidos += 1
                    
                    # 2. Verificar estructura temporal (fechas)
                    patrones_fechas = [
                        r'(19|20)\d\d\s*[-–]\s*((19|20)\d\d|presente|actualidad|actual|current|present)',
                        r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|sept|oct|nov|dic).{0,20}(\d{4})',
                        r'\d{2}\/\d{4}\s*[-–]\s*(\d{2}\/\d{4}|presente|actualidad|actual)',
                        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).{0,20}(\d{4})'
                    ]
                    
                    if any(re.search(patron, texto_lower) for patron in patrones_fechas):
                        criterios_cumplidos += 1
                    
                    # 3. Verificar empresas/cargos (con múltiples patrones)
                    patrones_empresa_cargo = [
                        r'(desarrollador|ingeniero|programador|analista|arquitecto).{0,50}(en|at|para|for|@).{0,30}([A-Z][a-zA-Z]+|[A-Z]{2,})',
                        r'([A-Z][a-zA-Z]+\s*(?:Inc|Ltd|LLC|S\.A\.|S\.L\.|GmbH|Corp|Co\.|Solutions|Technologies|Tech|Software|Systems|Digital))',
                        r'(senior|ssr|jr|junior|mid).{0,20}(desarrollador|developer|ingeniero|engineer)'
                    ]
                    
                    if any(re.search(patron, texto_cv) for patron in patrones_empresa_cargo):
                        criterios_cumplidos += 1
                    
                    # 4. Tecnologías relevantes mencionadas en contexto de experiencia
                    # Buscar tecnologías relevantes cerca de palabras de experiencia
                    tech_en_contexto = 0
                    for tech in tech_relevantes:
                        patrones_contexto = [
                            rf'(desarroll|implement|utiliz|us[eé]|trabaj|experiencia).{{0,50}}{re.escape(tech.lower())}',
                            rf'{re.escape(tech.lower())}.{{0,50}}(desarroll|implement|utiliz|us[eé]|trabaj|experiencia)'
                        ]
                        if any(re.search(patron, texto_lower) for patron in patrones_contexto):
                            tech_en_contexto += 1
                    
                    if tech_en_contexto >= 3:
                        criterios_cumplidos += 2
                    elif tech_en_contexto >= 1:
                        criterios_cumplidos += 1
                    
                    # 5. Orden cronológico inverso (más reciente primero)
                    # Extraer años y verificar si están en orden descendente
                    años = re.findall(r'(19|20)\d\d', texto_lower)
                    if len(años) >= 4:  # Necesitamos suficientes años para evaluar el orden
                        # Convertir a enteros y dividir en mitades
                        años_int = [int(a) for a in años]
                        primera_mitad = años_int[:len(años_int)//2]
                        segunda_mitad = años_int[len(años_int)//2:]
                        
                        # Verificar si la primera mitad tiene años más recientes en promedio
                        if sum(primera_mitad)/len(primera_mitad) > sum(segunda_mitad)/len(segunda_mitad):
                            criterios_cumplidos += 1



                elif seccion == "Habilidades":
                    # DETECCIÓN MEJORADA DE HABILIDADES TÉCNICAS
                    
                    # 1. Verificar presencia de tecnologías relevantes para el puesto
                    # Usar técnicas más robustas para detectar variaciones
                    tech_encontradas = []
                    for tech in tech_relevantes:
                        # Intentar diferentes variaciones de búsqueda
                        tech_lower = tech.lower()
                        patrones_tech = [
                            rf'\b{re.escape(tech_lower)}\b',  # Palabra exacta
                            rf'\b{re.escape(tech_lower)}[^\w]',  # Palabra con puntuación
                            rf'[^\w]{re.escape(tech_lower)}\b'  # Palabra con puntuación antes
                        ]
                        
                        if any(re.search(patron, texto_lower) for patron in patrones_tech):
                            tech_encontradas.append(tech)
                    
                    # Evaluar según el porcentaje de tecnologías encontradas
                    tech_porcentaje = len(tech_encontradas) / len(tech_relevantes) if tech_relevantes else 0
                    
                    if tech_porcentaje >= 0.5:  # 50% o más
                        criterios_cumplidos += 2
                    elif tech_porcentaje >= 0.25:  # 25% o más
                        criterios_cumplidos += 1
                    
                    # 2. Verificar habilidades técnicas (conceptos más generales)
                    skills_encontradas = []
                    for skill in habilidades_relevantes:
                        skill_words = skill.lower().split()
                        # Considerar match parcial si hay palabras significativas
                        palabras_significativas = [w for w in skill_words if len(w) > 3]
                        if palabras_significativas and any(re.search(rf'\b{re.escape(word)}\b', texto_lower) for word in palabras_significativas):
                            skills_encontradas.append(skill)
                    
                    skills_porcentaje = len(skills_encontradas) / len(habilidades_relevantes) if habilidades_relevantes else 0
                    
                    if skills_porcentaje >= 0.4:  # 40% o más
                        criterios_cumplidos += 2
                    elif skills_porcentaje >= 0.2:  # 20% o más
                        criterios_cumplidos += 1
                    
                    # 3. Organización de habilidades (varios patrones)
                    patrones_organizacion = [
                        r'(habilidades\s*técnicas|technical\s*skills|conocimientos|technologies|stack|competencias)',
                        r'(frontend|backend|fullstack|devops|cloud|database|mobile)',
                        r'(lenguajes|frameworks|librerías|herramientas|entornos|languages|tools|libraries)',
                        r'(programación|desarrollo|diseño|arquitectura|implementation|deployment)'
                    ]
                    
                    org_encontradas = sum(1 for patron in patrones_organizacion if re.search(patron, texto_lower))
                    if org_encontradas >= 2:
                        criterios_cumplidos += 1
                    elif org_encontradas >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 4. Nivel de experiencia en habilidades (común en buenos CVs)
                    patrones_nivel = [
                        r'(básico|basic|intermedio|intermediate|avanzado|advanced|experto|expert)',
                        r'(principiante|beginner|junior|mid|senior|master)',
                        r'([1-5]\s*\/\s*5|\d{1,2}\s*\/\s*10|\d{1,2}\s*años)'
                    ]
                    
                    if any(re.search(patron, texto_lower) for patron in patrones_nivel):
                        criterios_cumplidos += 1
                    
                    # 5. Actualidad de tecnologías (para puestos técnicos)
                    tech_recientes = []
                    tech_year_map = {
                        # Frontend
                        'react': 2020, 'angular': 2020, 'vue': 2020, 'typescript': 2020, 
                        'next.js': 2022, 'nuxt': 2022, 'svelte': 2022, 'tailwind': 2022,
                        # Backend
                        'node.js': 2020, 'django': 2020, 'flask': 2020, 'spring boot': 2020,
                        'fastapi': 2021, 'nestjs': 2021, 'graphql': 2021,
                        # DevOps/Cloud
                        'kubernetes': 2020, 'docker': 2020, 'aws': 2020, 'azure': 2020,
                        'github actions': 2021, 'terraform': 2021, 'microservices': 2021
                    }
                    
                    for tech, year in tech_year_map.items():
                        if re.search(rf'\b{re.escape(tech)}\b', texto_lower):
                            tech_recientes.append(tech)
                    
                    if len(tech_recientes) >= 3:
                        criterios_cumplidos += 1
                    
                    # 6. Para PDFs, compensar si tiene buen contenido técnico pero pierde formato
                    if es_pdf and factor_tecnico > 0.5 and criterios_cumplidos < criterios_total * 0.7:
                        criterios_cumplidos += 1


                elif seccion == "Educación":
                    # DETECCIÓN MEJORADA DE EDUCACIÓN
                    
                    # 1. Buscar instituciones educativas (ampliar patrones)
                    patrones_institucion = [
                        r'(universidad|university|instituto|college|escuela|school|academy|politécnic|polytechnic|faculty)',
                        r'(u\.\s*n\.\s*a\.\s*m|itesm|tec\s+de\s+monterrey|uam|uvm|la\s+salle|ibero|itam)',
                        r'(nacional|autónoma|complutense|harvard|stanford|mit|oxford|cambridge)',
                        r'(estudios|formación|formation|académica|education|educación)'
                    ]
                    
                    instituciones_encontradas = sum(1 for patron in patrones_institucion if re.search(patron, texto_lower))
                    if instituciones_encontradas >= 2:
                        criterios_cumplidos += 2
                    elif instituciones_encontradas >= 1:
                        criterios_cumplidos += 1
                    
                    # 2. Buscar titulaciones (ampliar patrones)
                    patrones_titulo = [
                        r'(licenciatura|grado|ingeniería|bachelor|engineering|título|maestría|máster|master|doctorado|phd|doctor)',
                        r'(técnico|superior|ingeniero|engineer|licenciado|graduado|egresado|diplomado|certificate|diploma)',
                        r'(carrera|degree|program|programa|b\.?s\.?|m\.?s\.?|ph\.?d\.?|ing\.?|lic\.?|m\.?b\.?a\.?)'
                    ]
                    
                    titulos_encontrados = sum(1 for patron in patrones_titulo if re.search(patron, texto_lower))
                    if titulos_encontrados >= 2:
                        criterios_cumplidos += 1
                    else:
                        # Buscar patrones compuestos que incluyan institución + título en la misma frase
                        for p_inst in patrones_institucion:
                            for p_tit in patrones_titulo:
                                if re.search(f'{p_inst}.{{0,50}}{p_tit}|{p_tit}.{{0,50}}{p_inst}', texto_lower):
                                    criterios_cumplidos += 1
                                    break
                            if criterios_cumplidos > 0:
                                break
                    
                    # 3. Buscar fechas asociadas con educación
                    patrones_fecha_edu = [
                        r'(universidad|university|instituto|college|grado|licenciatura|ingenier).{0,100}(19|20)\d\d',
                        r'(19|20)\d\d.{0,100}(universidad|university|instituto|college|grado|licenciatura)',
                        r'(graduad[oa]|egresad[oa]|titulad[oa]).{0,50}(19|20)\d\d'
                    ]
                    
                    if any(re.search(patron, texto_lower) for patron in patrones_fecha_edu):
                        criterios_cumplidos += 1
                    
                    # 4. Verificar relevancia para el puesto (área de estudio)
                    # Para cada puesto, áreas de estudio relevantes
                    areas_relevantes = {
                        "desarrollador": ["informática", "sistemas", "computación", "software", "desarrollo", "programación", "computer science", "it"],
                        "datos": ["datos", "estadística", "matemáticas", "análisis", "data science", "big data", "machine learning"],
                        "seguridad": ["seguridad", "ciberseguridad", "informática", "redes", "sistemas", "security"],
                        "cloud": ["sistemas", "informática", "redes", "cloud computing", "computación en la nube"],
                        "ingeniero": ["ingeniería", "sistemas", "informática", "electrónica", "telecomunicaciones", "engineering"]
                    }
                    
                    # Buscar áreas relevantes para el puesto
                    areas_para_puesto = []
                    for key, areas in areas_relevantes.items():
                        if key in puesto.lower():
                            areas_para_puesto.extend(areas)
                    
                    # Si no se encontró match específico, usar áreas generales de tecnología
                    if not areas_para_puesto:
                        areas_para_puesto = ["informática", "sistemas", "computación", "tecnología", "ingeniería", "computer", "technology"]
                    
                    # Buscar coincidencias con áreas relevantes
                    areas_encontradas = sum(1 for area in areas_para_puesto if re.search(rf'\b{re.escape(area)}\b', texto_lower))
                    if areas_encontradas >= 2:
                        criterios_cumplidos += 1
                    elif areas_encontradas >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 5. Verificar estructura y organización
                    if re.search(r'(universidad|university|instituto|college).{0,100}(licenciatura|grado|ingeniería).{0,100}(19|20)\d\d', texto_lower, re.DOTALL):
                        criterios_cumplidos += 1
                        
                elif seccion == "Certificados":
                    # DETECCIÓN MEJORADA DE CERTIFICACIONES
                    
                    # 1. Buscar certificaciones específicas para el puesto
                    certificaciones_relevantes = conocimiento_puesto.get("certificaciones_valoradas", [])
                    cert_encontradas = []
                    
                    for cert in certificaciones_relevantes:
                        # Palabras clave de la certificación
                        cert_words = cert.lower().split()
                        palabras_significativas = [w for w in cert_words if len(w) > 3]
                        
                        # Buscar coincidencias con palabras significativas
                        if any(re.search(rf'\b{re.escape(word)}\b', texto_lower) for word in palabras_significativas):
                            cert_encontradas.append(cert)
                    
                    # Evaluar según el número de certificaciones encontradas
                    if certificaciones_relevantes:
                        if len(cert_encontradas) >= 2:
                            criterios_cumplidos += 2
                        elif len(cert_encontradas) >= 1:
                            criterios_cumplidos += 1
                    
                    # 2. Buscar certificadoras y plataformas conocidas
                    certificadoras = [
                        r'(microsoft|aws|google|ibm|cisco|oracle|sap|comptia|itil|pmi|scrum|safe|isaca|isc2|ec-council)',
                        r'(coursera|udemy|edx|platzi|datacamp|pluralsight|linkedin\s+learning|udacity|openwebinars)',
                        r'(certified|certification|certificación|certificado|diploma|acreditación|credential)',
                        r'(ceh|cissp|ccna|ccnp|ccie|mcsa|mcse|mcp|aws[\s-]?sa|azure[\s-]?admin|gcp)'
                    ]
                    
                    certificadoras_encontradas = sum(1 for patron in certificadoras if re.search(patron, texto_lower))
                    if certificadoras_encontradas >= 2:
                        criterios_cumplidos += 1
                    elif certificadoras_encontradas >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 3. Buscar detalles específicos de certificaciones
                    
                    # 3.1 Fechas de certificación
                    if re.search(r'(certificación|certificado|curso|diploma).{0,50}(19|20)\d\d', texto_lower):
                        criterios_cumplidos += 1
                    
                    # 3.2 Instituciones emisoras
                    if re.search(r'(emitido|otorgado|expedido|issued).{0,30}(por|by)', texto_lower):
                        criterios_cumplidos += 0.5
                    
                    # 4. Buscar formación complementaria
                    patrones_formacion = [
                        r'(bootcamp|workshop|taller|diplomado|specialization|nanodegree)',
                        r'(formación complementaria|formación adicional|ongoing education|continuing education)',
                        r'(curso|course|training|capacitación).{0,50}(online|presencial|virtual|a distancia)'
                    ]
                    
                    formacion_encontrada = sum(1 for patron in patrones_formacion if re.search(patron, texto_lower))
                    if formacion_encontrada >= 2:
                        criterios_cumplidos += 1
                    elif formacion_encontrada >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 5. Evaluación específica para perfiles técnicos sin certificaciones formales
                    # Muchos desarrolladores experimentados no tienen certificaciones pero sí proyectos
                    if "desarrollador" in puesto.lower() or "programador" in puesto.lower() or "ingeniero" in puesto.lower():
                        patrones_proyectos = [
                            r'(github|gitlab|bitbucket).{0,50}(proyecto|repositorio|development|código)',
                            r'(proyecto personal|side project|open source|contribución|hackathon)',
                            r'(desarrollé|implementé|creé|diseñé).{0,50}(usando|utilizando|con).{0,50}(tecnologías|stack)'
                        ]
                        
                        proyectos_encontrados = sum(1 for patron in patrones_proyectos if re.search(patron, texto_lower))
                        if proyectos_encontrados >= 2:
                            criterios_cumplidos += 1  # Compensar falta de certificaciones con proyectos
                    
                        
                elif seccion == "Idiomas":
                    # DETECCIÓN MEJORADA DE IDIOMAS
                    
                    # 1. Buscar mención de idiomas comunes con patrones más flexibles
                    patrones_idiomas = [
                        r'(inglés|english|español|spanish|francés|french|alemán|german|italiano|italian|portugués|portuguese|chino|chinese|japonés|japanese)',
                        r'(idiomas|languages|lenguas|conocimientos\s+de\s+idiomas|language\s+skills)',
                        r'(natal|nativo|native|materno|mother\s+tongue|lengua\s+materna)'
                    ]
                    
                    idiomas_encontrados = sum(1 for patron in patrones_idiomas if re.search(patron, texto_lower))
                    if idiomas_encontrados >= 2:
                        criterios_cumplidos += 1
                    elif idiomas_encontrados >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 2. Buscar niveles de competencia con varios sistemas
                    
                    # 2.1 Marco Común Europeo (más variaciones de búsqueda)
                    patrones_mcer = [
                        r'(A1|A2|B1|B2|C1|C2).{0,20}(inglés|español|francés|alemán|italiano|portugués)',
                        r'(inglés|español|francés|alemán|italiano|portugués).{0,20}(A1|A2|B1|B2|C1|C2)',
                        r'(MCER|CEFR|Marco\s+Común|Common\s+Framework).{0,30}(A1|A2|B1|B2|C1|C2)'
                    ]
                    
                    mcer_encontrado = any(re.search(patron, texto_lower) for patron in patrones_mcer)
                    if mcer_encontrado:
                        criterios_cumplidos += 1
                    
                    # 2.2 Descriptores comunes de nivel (más variaciones)
                    patrones_nivel = [
                        r'(básico|basic|elemental|beginner|principiante)',
                        r'(intermedio|intermediate|medio|regular)',
                        r'(avanzado|advanced|alto|high|fluido|fluent)',
                        r'(bilingüe|bilingual|nativo|native)',
                        r'(nivel\s+conversacional|business\s+level|profesional|professional|técnico|technical)'
                    ]
                    
                    niveles_encontrados = sum(1 for patron in patrones_nivel if re.search(patron, texto_lower))
                    if niveles_encontrados >= 2:
                        criterios_cumplidos += 1
                    elif niveles_encontrados >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 3. Verificar mención específica de inglés (crucial en tecnología)
                    patrones_ingles = [
                        r'(inglés|english).{0,20}(B2|C1|C2|avanzado|advanced|fluido|fluent|bilingüe|bilingual|nativo|native|profesional|business)',
                        r'(técnico|technical|conversacional|business).{0,20}(inglés|english)',
                        r'(inglés|english).{0,20}(comprensión|lectura|escrito|oral)'
                    ]
                    
                    ingles_avanzado = any(re.search(patron, texto_lower) for patron in patrones_ingles)
                    if ingles_avanzado:
                        criterios_cumplidos += 2  # Dar más peso al inglés avanzado
                    elif re.search(r'(inglés|english).{0,20}(B1|intermedio|intermediate|medio)', texto_lower):
                        criterios_cumplidos += 1  # Inglés intermedio
                    elif re.search(r'(inglés|english)', texto_lower):
                        criterios_cumplidos += 0.5  # Al menos menciona inglés
                    
                    # 4. Buscar certificaciones de idiomas
                    patrones_cert_idiomas = [
                        r'(TOEFL|IELTS|TOEIC|Cambridge|FCE|CAE|CPE|DELE|DELF|DALF|Goethe|TestDaF)',
                        r'(certificación|certificado|certificate).{0,30}(inglés|english|español|français|alemán)',
                        r'(score|puntaje|result|band).{0,20}(\d{2,3}\/\d{3}|\d{1,2}\.\d{1,2})'
                    ]
                    
                    cert_idiomas = any(re.search(patron, texto_lower) for patron in patrones_cert_idiomas)
                    if cert_idiomas:
                        criterios_cumplidos += 1
                    
                    # 5. Detectar descripciones de capacidades específicas
                    patrones_capacidades = [
                        r'(lectura|reading|escritura|writing|habla|speaking|escucha|listening|comprensión|comprehension)',
                        r'(oral|escrito|written|conversación|conversation|redacción|drafting)',
                        r'(comunicación|communication|reuniones|meetings|presentaciones|presentations)'
                    ]
                    
                    capacidades_encontradas = sum(1 for patron in patrones_capacidades if re.search(patron, texto_lower))
                    if capacidades_encontradas >= 2:
                        criterios_cumplidos += 1
                    elif capacidades_encontradas >= 1:
                        criterios_cumplidos += 0.5
                    
                    # 6. Compensación para perfiles técnicos (el inglés es implícito)
                    if "desarrollador" in puesto.lower() and factor_tecnico > 0.7 and criterios_cumplidos < 3:
                        criterios_cumplidos += 1
            
                elif seccion == "Datos":
                    # EVALUACIÓN MÁS ESTRICTA PARA LA SECCIÓN "DATOS"
                    # Implementación mejorada para detectar información de contacto en CV
                    
                    criterios_cumplidos = 0
                    criterios_total = 5  # Cinco criterios en total
                    
                    # 1. Nombre completo (detectar nombres con formato moderno)
                    patrones_nombre = [
                        r'[Nn]ombre:?\s*[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+\s+[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+(\s+[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?',
                        r'^[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+\s+[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+(\s+[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?',  # Al inicio del CV
                        r'[📝👤🧑📋🪪]\s*[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+\s+[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+',  # Con emojis
                    ]
                    
                    tiene_nombre_completo = any(re.search(patron, texto_cv) for patron in patrones_nombre)
                    # Verificar si tiene al menos un nombre básico
                    tiene_nombre_basico = re.search(r'[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+\s+[A-Z]?', texto_cv) is not None
                    
                    if tiene_nombre_completo:
                        criterios_cumplidos += 1
                    elif tiene_nombre_basico:
                        criterios_cumplidos += 0.5  # Crédito parcial por nombre básico
                    
                    # 2. Email profesional (detectar con y sin emojis)
                    patrones_email = [
                        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Patrón básico de email
                        r'(email|correo|e-mail|mail)[:;]?\s*[a-zA-Z0-9._%+-]+@',  # Con etiqueta
                        r'[📧✉️📩📨🔹]\s*[a-zA-Z0-9._%+-]+@'  # Con emojis
                    ]
                    
                    # Verificar si es un email profesional vs. genérico
                    tiene_email = False
                    email_match = None
                    
                    for patron in patrones_email:
                        match = re.search(patron, texto_cv)
                        if match:
                            tiene_email = True
                            # Extraer el email para ver si es genérico
                            email_text = texto_cv[match.start():match.start()+100]  # Tomar suficiente contexto
                            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email_text)
                            if email_match:
                                email_match = email_match.group(0).lower()
                            break
                    
                    if tiene_email:
                        criterios_cumplidos += 1
                        
                        # Bonus por email profesional (no genérico - no gmail, hotmail, etc.)
                        if email_match and not any(domain in email_match for domain in ['@gmail', '@hotmail', '@yahoo', '@outlook']):
                            criterios_cumplidos += 0.3
                    
                    # 3. Teléfono (detectar con y sin emojis)
                    patrones_telefono = [
                        r'(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}',  # Patrón básico internacional
                        r'\d{2,3}[\s.-]?\d{2,3}[\s.-]?\d{2,3}([\s.-]?\d{2,3})?',  # Patrón local
                        r'(teléfono|telefono|celular|móvil|tel|phone|contacto)[:;]?\s*(\+?\d|\(\d)',  # Con etiqueta
                        r'[📞📱☎️📴📳]\s*\+?\d'  # Con emojis
                    ]
                    
                    tiene_telefono = any(re.search(patron, texto_cv) for patron in patrones_telefono)
                    if tiene_telefono:
                        criterios_cumplidos += 1
                    
                    # 4. Perfiles profesionales (LinkedIn, GitHub, etc.)
                    patrones_linkedin = [
                        r'linkedin\.com\/in\/[a-zA-Z0-9_-]+',
                        r'linkedin\.com\/[a-zA-Z0-9_/-]+',
                        r'(linkedin|in)[:;\s]+[a-zA-Z0-9_/-]+'
                    ]
                    
                    patrones_github = [
                        r'github\.com\/[a-zA-Z0-9_-]+',
                        r'(github|gh)[:;\s]+[a-zA-Z0-9_/-]+'
                    ]
                    
                    patrones_web = [
                        r'(portfolio|portafolio|website|sitio|web|blog)[:;\s]+[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                        r'http[s]?:\/\/[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    ]
                    
                    # Verificar cada tipo de perfil
                    tiene_linkedin = any(re.search(patron, texto_cv, re.IGNORECASE) for patron in patrones_linkedin)
                    tiene_github = any(re.search(patron, texto_cv, re.IGNORECASE) for patron in patrones_github)
                    tiene_web = any(re.search(patron, texto_cv, re.IGNORECASE) for patron in patrones_web)
                    
                    # Contar perfiles profesionales
                    perfiles_profesionales = 0
                    
                    if tiene_linkedin:
                        perfiles_profesionales += 1
                        criterios_cumplidos += 0.5
                        
                    if tiene_github:
                        perfiles_profesionales += 1
                        criterios_cumplidos += 0.5
                        
                    if tiene_web:
                        perfiles_profesionales += 1
                        criterios_cumplidos += 0.5
                    
                    # 5. Ubicación o ciudad (útil para reclutadores)
                    patrones_ubicacion = [
                        r'(ciudad|ubicación|location|dirección|address|city)[:;]?\s*[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+',  # Con etiqueta
                        r'[📍🌍🌎🌏🏙️]\s*[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+',  # Con emojis
                        r'\b[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+,\s*[A-Z][a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b'  # Ciudad, País
                    ]
                    
                    tiene_ubicacion = any(re.search(patron, texto_cv) for patron in patrones_ubicacion)
                    if tiene_ubicacion:
                        criterios_cumplidos += 0.5
                    
                    # EVALUACIÓN MÁS ESTRICTA: No normalizar automáticamente los criterios cumplidos
                    # En su lugar, aplicar reglas específicas para la puntuación final
                    
                    # Evaluación basada en componentes críticos
                    if tiene_nombre_completo and tiene_email and tiene_telefono and perfiles_profesionales >= 2 and tiene_ubicacion:
                        # Información completa y profesional - Puntuación máxima (10/10)
                        puntos = max_puntos
                        feedback = "✅ Excelente: Información de contacto completa y bien presentada"
                    elif tiene_nombre_completo and tiene_email and tiene_telefono and perfiles_profesionales >= 1:
                        # Información muy buena pero falta algo (8/10)
                        puntos = int(max_puntos * 0.8)
                        feedback = "✅ Muy bueno: Información de contacto casi completa"
                    elif tiene_email and tiene_telefono and (tiene_nombre_completo or perfiles_profesionales >= 1):
                        # Información buena pero no completa (7/10)
                        puntos = int(max_puntos * 0.7)
                        feedback = "✅ Bueno: Optimiza la presentación de contacto"
                    elif tiene_email and tiene_telefono:
                        # Información básica (6/10) - Solo lo mínimo
                        puntos = int(max_puntos * 0.6)
                        feedback = "⚠️ Aceptable: Información de contacto básica"
                    elif (tiene_email or tiene_telefono) and tiene_nombre_basico:
                        # Información insuficiente (4/10)
                        puntos = int(max_puntos * 0.4)
                        feedback = "⚠️ Regular: Información de contacto incompleta"
                    else:
                        # Prácticamente sin información (2/10)
                        puntos = int(max_puntos * 0.2)
                        feedback = "❌ Deficiente: Completa tu información de contacto"
                    
                    # Si tiene muchos emojis de contacto y formato moderno, dar bonus (pero sin exceder max_puntos)
                    if tiene_emojis and sum(1 for emoji in '📧📞📱🔗🌐💼📍🐙✉️☎️🏙️🚀' if emoji in texto_cv) >= 3:
                        puntos = min(puntos + 1, max_puntos)
                    
                    # Asegurar que el puntaje esté dentro de los límites
                    puntos = max(1, min(puntos, max_puntos))





               #Calcular puntos basados en criterios_cumplidos y presencia de keywords
                factor_keywords = presentes / len(keywords) if len(keywords) > 0 else 0
                factor_criterios = criterios_cumplidos / criterios_total if criterios_total > 0 else 0
                
                # Ponderación: 30% keywords, 70% criterios específicos
                if es_pdf:
                    ponderacion = factor_keywords * 0.2 + factor_criterios * 0.8
                else:
                    ponderacion = factor_keywords * 0.3 + factor_criterios * 0.7

                puntos = round(ponderacion * max_puntos)
                puntos = min(max_puntos, max(1, puntos))  # Asegurar rango válido


            porcentaje = (puntos / max_puntos) * 100
            # Determinar mensaje basado en puntuación
            if puntos >= max_puntos * 0.8:
                mensaje = datos["mensaje_excelente"]
                feedback = "✅ Completo"
            elif puntos >= max_puntos * 0.6:
                mensaje = datos["mensaje_bueno"]
                feedback = "✅ Completo"
            elif puntos >= max_puntos * 0.4:
                mensaje = datos["mensaje_regular"]
                feedback = "⚠️ Faltan elementos"
            else:
                mensaje = datos["mensaje_mejorable"]
                feedback = "⚠️ Faltan elementos"
        
            puntos = max(1, min(round(puntos), max_puntos))

            porcentaje = (puntos / max_puntos) * 100

            # Nueva lógica de feedback más precisa
            if porcentaje >= 95:  # El máximo, debe estar casi perfecto
                mensaje = datos["mensaje_excelente"]
                feedback = "✅ Excelente"
            elif porcentaje >= 85:  # Muy bueno, pero no perfecto
                mensaje = datos["mensaje_excelente"]
                feedback = "✅ Muy bueno"
            elif porcentaje >= 70:  # Bueno
                mensaje = datos["mensaje_bueno"]
                feedback = "✅ Bueno"
            elif porcentaje >= 60:  # Aceptable
                mensaje = datos["mensaje_regular"]
                feedback = "⚠️ Aceptable"
            elif porcentaje >= 40:  # Regular
                mensaje = datos["mensaje_regular"]
                feedback = "⚠️ Regular"
            else:  # Deficiente
                mensaje = datos["mensaje_mejorable"]
                feedback = "❌ Deficiente"

            
            # Detallar el feedback para cada sección
            if seccion == "Perfil":
                if porcentaje < 60:
                    feedback += ": Define mejor tu perfil profesional"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Se puede mejorar el enfoque"
                    
            elif seccion == "Experiencia":
                if porcentaje < 60:
                    feedback += ": Falta detallar experiencias relevantes"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Añade más logros medibles"
                    
            elif seccion == "Habilidades":
                if porcentaje < 60:
                    feedback += ": Incluye más habilidades específicas"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Organiza mejor tus habilidades"
                    
            elif seccion == "Certificados":
                if porcentaje < 60:
                    feedback += ": Añade certificaciones relevantes"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Complementa con más certificaciones"
                    
            elif seccion == "Idiomas":
                if porcentaje < 60:
                    feedback += ": Especifica mejor tus niveles de idiomas"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Detalla competencias específicas"
                    
            elif seccion == "Datos":
                if porcentaje < 60:
                    feedback += ": Completa tu información de contacto"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Optimiza la presentación de contacto"
                    
            elif seccion == "Formato":
                if porcentaje < 60:
                    feedback += ": Mejora la estructura y organización"
                elif porcentaje < 90 and porcentaje >= 70:
                    feedback += ": Afina el diseño para mayor legibilidad"


        # Crear entrada en resultados (estructura compatible con tu HTML)
        resultados.append((
            seccion,          # 1. Nombre sección (str)
            puntos,          # 2. Puntos obtenidos (int)
            max_puntos,      # 3. Máximo posible (int)
            feedback         # 4. Feedback simple (str)
        ))  # <- ¡Solo 4 elementos, como necesitas!
        
        # Sumar al puntaje total (sin exceder el máximo global de 100)
        puntaje_total += puntos
        

    # === AJUSTES FINALES PARA CUALQUIER TIPO DE CV ===
    
    # 1. Verificar si es un CV técnicamente completo pero con algunas debilidades formales
    if factor_tecnico > 0.7:  # CV con excelente contenido técnico
        # Identificar 2 secciones con menor puntaje relativo
        # Calculamos un "deficit score" para cada sección: qué tan lejos está del máximo posible
        deficits = [(idx, 1 - (puntos / max_puntos)) for idx, (seccion, puntos, max_puntos, _) in enumerate(resultados)]
        deficits.sort(key=lambda x: x[1], reverse=True)  # Ordenar por mayor déficit
        
        # Mejorar 2 secciones con el mayor déficit
        for i, (idx, deficit) in enumerate(deficits[:2]):
            if deficit > 0.3:  # Solo mejorar secciones que estén por debajo del 70% de su máximo
                seccion, puntos, max_puntos, _ = resultados[idx]
                mejora = min(max_puntos * 0.2, 3)  # Mejorar hasta un 20% del máximo, o 3 puntos como límite
                nuevos_puntos = min(puntos + mejora, max_puntos)
                
                # CORRECCIÓN 2: No marcar como "Completo" si no llega al 100%
                # Solo actualizar feedback si mejora significativamente
                if nuevos_puntos >= max_puntos * 0.6 and puntos < max_puntos * 0.6:
                    porcentaje_nuevo = (nuevos_puntos / max_puntos) * 100
                    if porcentaje_nuevo >= 95:
                        nuevo_feedback = "✅ Excelente"
                    elif porcentaje_nuevo >= 85:
                        nuevo_feedback = "✅ Muy bueno"
                    elif porcentaje_nuevo >= 70:
                        nuevo_feedback = "✅ Bueno"
                    else:
                        nuevo_feedback = "⚠️ Aceptable"
                        
                    resultados[idx] = (seccion, nuevos_puntos, max_puntos, nuevo_feedback)
                else:
                    resultados[idx] = (seccion, nuevos_puntos, max_puntos, feedback)
                
                puntaje_total += (nuevos_puntos - puntos)
    
    # 2. Compensación para CVs extraídos de PDFs (que pueden perder formato en el proceso)
    if es_pdf:
        # Identificar secciones probablemente afectadas por extracción de PDF
        secciones_afectadas = ["Formato", "Perfil"]
        
        for idx, (seccion, puntos, max_puntos, feedback) in enumerate(resultados):
            if seccion in secciones_afectadas and puntos < max_puntos * 0.6:
                # Calcular mejora proporcional al contenido técnico
                mejora = min(max_puntos * 0.15, 2) * min(1.0, factor_tecnico + 0.3)
                nuevos_puntos = min(puntos + mejora, max_puntos * 0.7)  # Máximo 70% del máximo posible
                
                if nuevos_puntos >= max_puntos * 0.6 and puntos < max_puntos * 0.6:
                    porcentaje_nuevo = (nuevos_puntos / max_puntos) * 100
                    if porcentaje_nuevo >= 95:
                        nuevo_feedback = "✅ Excelente"
                    elif porcentaje_nuevo >= 85:
                        nuevo_feedback = "✅ Muy bueno"
                    elif porcentaje_nuevo >= 70:
                        nuevo_feedback = "✅ Bueno"
                    else:
                        nuevo_feedback = "⚠️ Aceptable"
                        
                    resultados[idx] = (seccion, nuevos_puntos, max_puntos, nuevo_feedback)
                else:
                    resultados[idx] = (seccion, nuevos_puntos, max_puntos, feedback)
                
                puntaje_total += (nuevos_puntos - puntos)
    
    # 3. Compensación para CVs con formato moderno que pueden no seguir convenciones estándar
    if tiene_emojis or re.search(r'[\U0001F300-\U0001F6FF]\s', primeras_lineas):
        for idx, (seccion, puntos, max_puntos, feedback) in enumerate(resultados):
            if seccion == "Formato" and puntos < max_puntos * 0.8:
                # Mejorar formato para CVs con diseño moderno
                nuevos_puntos = min(max_puntos, puntos + max_puntos * 0.2)  # CORRECCIÓN 2: Menos mejora, antes era 0.4
                
                # CORRECCIÓN 2: Usar un feedback más preciso basado en porcentaje
                porcentaje_nuevo = (nuevos_puntos / max_puntos) * 100
                if porcentaje_nuevo >= 95:
                    nuevo_feedback = "✅ Excelente: Formato moderno y atractivo"
                elif porcentaje_nuevo >= 85:
                    nuevo_feedback = "✅ Muy bueno: Diseño visual efectivo"
                else:
                    nuevo_feedback = "✅ Bueno: Formato moderno"
                    
                resultados[idx] = (seccion, nuevos_puntos, max_puntos, nuevo_feedback)
                puntaje_total += (nuevos_puntos - puntos)
                break  # Solo ajustar una vez
    
    # 4. Evaluar relevancia global para el puesto y ajustar puntaje final
    relevancia_global = factor_tecnico  # Ya calculado antes
    
    # Umbral de excelencia técnica
    if relevancia_global > 0.85:  # Extremadamente adecuado para el puesto
        # Garantizar un mínimo de 85 puntos para CVs altamente relevantes
        puntaje_total = max(puntaje_total, 85)
    elif relevancia_global > 0.75:  # Muy adecuado para el puesto
        # Garantizar un mínimo de 80 puntos
        puntaje_total = max(puntaje_total, 80)
    elif relevancia_global > 0.65:  # Bastante adecuado para el puesto
        # Garantizar un mínimo de 70 puntos
        puntaje_total = max(puntaje_total, 70)
    
    # 5. Limitar puntaje total a 100
    puntaje_total = min(100, round(puntaje_total))
    
    # Asegurar que todos los puntos estén redondeados
    resultados = [(seccion, round(puntos), max_puntos, feedback) for seccion, puntos, max_puntos, feedback in resultados]
    
    

    # Añade esta verificación adicional inmediatamente antes de la línea con "return puntaje_total, resultados"
    # en la función evaluar_cv

    # Corrección específica para CVs con información de contacto completa pero que reciben puntuación baja
    for idx, (seccion, puntos, max_puntos, feedback) in enumerate(resultados):
        if seccion == "Datos":
            # Verificar si el CV realmente tiene todos los elementos esenciales
            tiene_todos_elementos = (
                re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto_cv) and  # Email
                re.search(r'(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}', texto_cv) and  # Teléfono
                re.search(r'linkedin\.com\/in\/[a-zA-Z0-9_-]+', texto_cv, re.IGNORECASE) and  # LinkedIn
                (re.search(r'github\.com\/[a-zA-Z0-9_-]+', texto_cv, re.IGNORECASE) or  # GitHub u otro perfil
                re.search(r'[a-zA-Z0-9][a-zA-Z0-9-]{1,61}\.[a-zA-Z]{2,}', texto_cv))  # Web personal
            )
            
            # Si tiene emojis y múltiples líneas de contacto, probablemente es un CV moderno muy completo
            tiene_formato_moderno = (
                tiene_emojis and
                re.search(r'📧|📞|🌐|📍|🐙|💼|📱|🚀', texto_cv) and
                len(re.findall(r'@|linkedin|github|\+\d{1,2}', primeras_lineas)) >= 3
            )
            
            # Si cumple alguna de las condiciones, establecer puntuación completa
            if tiene_todos_elementos or tiene_formato_moderno:
                nuevo_puntos = max_puntos  # Establecer a puntuación máxima (10/10)
                
                # Actualizar resultados y puntaje total
                if puntos < nuevo_puntos:
                    puntaje_total += (nuevo_puntos - puntos)
                    resultados[idx] = (seccion, nuevo_puntos, max_puntos, "✅ Excelente: Información de contacto completa y bien presentada")
            
            break  # Solo necesitamos revisar la sección "Datos"


    return puntaje_total, resultados








# === Rutas ===
@app.get("/", response_class=HTMLResponse)
async def mostrar_formulario(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "resultado": None,
        "error": None,
        "detalles": [],
        "recomendaciones": [],
        "contenido_cv": "",
        "nombre": "",
        "puesto": ""
    })


@app.post("/subir", response_class=HTMLResponse)
async def procesar_cv(request: Request, archivo: UploadFile = File(...), puesto: str = Form(...)):
    try:
        if not puesto or puesto.strip() == "" or puesto.startswith("--"):
            raise ValueError("Debes seleccionar un puesto válido del menú desplegable")
        
        if not archivo.filename.lower().endswith((".pdf", ".docx")):
            raise ValueError("Solo se aceptan archivos PDF o DOCX")
            
        print(f"🔄 Procesando archivo: {archivo.filename} para puesto: {puesto}")
        texto = await procesar_archivo(archivo)
        print(f"✅ Archivo procesado: {len(texto)} caracteres extraídos")
        
        print("🔄 Evaluando CV...")
        puntaje, detalles = await evaluar_cv(texto, puesto)
        print(f"✅ Evaluación completada: {puntaje}/100 puntos")
        
        print("🔄 Generando recomendaciones...")
        recomendaciones = await generar_recomendaciones(puesto, texto)
        print(f"✅ Recomendaciones generadas: {len(recomendaciones)} items")

        # CORRECCIÓN: Cambiar recomendaciones_texto por recomendaciones
        # Procesar las recomendaciones para asignar títulos únicos
        recomendaciones_con_titulos = []
        titulos_usados = set()
        
        for i, rec in enumerate(recomendaciones):
            rec_lower = rec.lower()
            titulo = None
            
            if "perfil" in rec_lower and "Perfil" not in titulos_usados:
                titulo = "Perfil"
            elif ("educación" in rec_lower or "formación" in rec_lower) and "Educación" not in titulos_usados:
                titulo = "Educación"
            elif ("habilidades" in rec_lower or "tecnologías" in rec_lower) and "Habilidades" not in titulos_usados:
                titulo = "Habilidades"
            elif "experiencia" in rec_lower and "Experiencia" not in titulos_usados:
                titulo = "Experiencia"
            elif ("certificaciones" in rec_lower or "certificados" in rec_lower) and "Certificados" not in titulos_usados:
                titulo = "Certificados"
            elif ("idiomas" in rec_lower or "inglés" in rec_lower) and "Idiomas" not in titulos_usados:
                titulo = "Idiomas"
            elif ("contacto" in rec_lower or "datos" in rec_lower) and "Datos" not in titulos_usados:
                titulo = "Datos"
            elif ("organiza" in rec_lower or "estructura" in rec_lower or "formato" in rec_lower) and "Formato" not in titulos_usados:
                titulo = "Formato"
            else:
                titulo = f"Recomendación {i+1}"
                
            if titulo:
                titulos_usados.add(titulo)
                
            recomendaciones_con_titulos.append((titulo, rec))

        return templates.TemplateResponse("index.html", {
            "request": request,
            "resultado": puntaje,
            "detalles": detalles,
            "nombre": archivo.filename,
            "contenido_cv": texto[:15000] + ("..." if len(texto) > 15000 else ""),
            "recomendaciones": recomendaciones,
            "puesto": puesto
        })
    except Exception as e:
        print(f"⚠️ Error en procesar_cv: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Error: {str(e)}"
        })



# === No cache ===
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response