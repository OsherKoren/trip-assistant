# Architecture

## System Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────┐
│   Frontend  │────▶│ API Gateway │────▶│     Lambda Function         │
│  (React/S3) │◀────│   (HTTP)    │◀────│  (FastAPI + LangGraph)      │
└─────────────┘     └─────────────┘     └─────────────────────────────┘
                                               │
                                        ┌──────┴──────┐
                                        │     S3      │
                                        │ (documents) │
                                        └─────────────┘
```

## Agent Graph Flow

```
START
  │
  ▼
┌─────────────────┐
│   Classifier    │  ← Determines topic from question
│     Node        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router (Edge)  │  ← Conditional edge based on category
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌─────────┐ ┌──────────┐
│Flights│ │Hotels │ │Car Rent │ │Itinerary │
│ Node  │ │ Node  │ │  Node   │ │  Node    │
└───┬───┘ └───┬───┘ └────┬────┘ └────┬─────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
                    │
                    ▼
                   END
```

## Data Flow

1. **User asks question** → Frontend sends to API Gateway
2. **API Gateway** triggers Lambda
3. **Lambda** runs FastAPI + LangGraph agent
4. **Classifier node** determines topic (flights/hotels/car/itinerary)
5. **Router** selects specialist node based on topic
6. **Specialist node** uses relevant document context, generates answer
7. **Response** flows back through API Gateway to frontend

## Topic Categories

| Category | Document | Example Questions |
|----------|----------|-------------------|
| flights | flights.txt | "What time is our flight?" |
| hotels | hotels.txt | "Where do we stay in Annecy?" |
| car_rental | car_rental.txt | "What's the booking number?" |
| itinerary | itinerary.txt | "What's planned for July 10?" |

## Technology Choices

| Component | Technology | Why |
|-----------|------------|-----|
| Agent | LangGraph 1.x | Learning target, native routing |
| LLM | OpenAI GPT-4o-mini | Cost-effective |
| API | FastAPI + Mangum | Lambda-compatible |
| Frontend | React + Tailwind | Simple, hosts on S3 |
| Deploy | AWS Lambda | FREE tier, pay-per-use |

## AWS Services (Cheap Stack)

| Service | Purpose | Cost |
|---------|---------|------|
| Lambda | Agent + API | FREE (1M req/month) |
| API Gateway | HTTP endpoint | FREE (1M req/month) |
| S3 | Frontend hosting | FREE (5GB) |
| CloudFront | CDN for frontend | FREE (1TB/month) |
| Parameter Store | API keys | FREE |
| CloudWatch | Logs | ~$0 |

**Estimated monthly cost: $0-5**
