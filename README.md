# 🏛️ E-Portal for Case Management and Hearings

**(Recognized as Patent by Government of India)**

A scalable, modern platform simplifying civil mediation and hearings, reducing operational costs by 99% compared to traditional processes. Built with Django Rest Framework, Vue.js, WebRTC, OpenAI integrations, and deployed on AWS infrastructure.

---

## 🚀 Features

- **End-to-End Case Management**  
  Clients can register, manage, and track their cases with secure document uploads and real-time notifications.

- **Scheduling & Mediation**  
  Efficiently schedule hearings, assign mediators, and track timelines.

- **Secure Video Conferencing**  
  Complete hosting control for mediators and lawyers, using a secure video service.

- **Notifications & Updates**  
  Real-time alerts for users and staff.

- **AI-Powered Features**  
  Integrated natural language understanding and summarization for case documents using OpenAI.

- **Scalable Microservices Architecture**  
  Built to handle large volumes of data and sessions reliably.

---

## 🏗️ Architecture

![architecture](https://github.com/user-attachments/assets/5deab73f-0e42-4f9f-95d2-d7bd43a6625a)


- **Nginx Ingress** to route client requests  
- **Kong API Gateway** to manage and authenticate requests  
- **Microservices**:
  - User Service
  - Case Service
  - Scheduling Service
  - Video Service
  - AI Service
  - Notification Service
  - Payment Service
- **Databases**: PostgreSQL for all services  
- **Kafka**: Event streaming and messaging  
- **Redis**: Caching and session storage  

---

## 📁 Project Structure

```plaintext
services/
  ├── ai_service/           # DRF project for AI workflows
  ├── case_service/         # DRF project for case and document management
  ├── frontend/             # Vue.js + Tailwind frontend
  ├── gateway/              # Kong configuration and ingress rules
  ├── notification_service/ # DRF project for notifications
  ├── payment_service/      # DRF project for handling payments
  ├── schedule_service/     # DRF project for scheduling
  └── video_service/        # DRF/WebRTC video session handling
