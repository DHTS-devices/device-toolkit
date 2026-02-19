# WHOOP External Resources

This page documents useful public resources for integrating WHOOP into research and software systems.

The goal is not to reverse engineer the device, but to enable reproducible and compliant data collection workflows.

---

## 1. Official Developer Platform

WHOOP provides a cloud-based developer API for accessing processed physiological data.

Official Documentation:
https://developer.whoop.com/

### Capabilities
| Feature | Available |
|------|------|
| Recovery scores | Yes |
| Sleep data | Yes |
| Workouts | Yes |
| Strain metrics | Yes |
| HRV | Yes |
| Respiratory rate | Yes |
| Raw PPG | No |
| Raw accelerometer | No |

### Access Method
WHOOP uses OAuth2 Authorization Code Flow.

Typical pipeline:

Device → Phone → WHOOP Cloud → API → Research Database

This means WHOOP acts as a physiological analytics platform rather than a raw sensor device.

---

## 2. Community API Clients

These repositories demonstrate how to connect to the WHOOP cloud API using Python or web applications.

They are useful for learning authentication flow and request structure.

---

### Example Projects

#### whoomp
https://github.com/jogolden/whoomp

Purpose:
- Demonstrates communication patterns with WHOOP services
- Useful for understanding data structure and device behavior

Recommended usage:
- Educational reference
- Data interpretation understanding
- Not required for production integration

---

#### WHOOP API ecosystem (GitHub topic)
https://github.com/topics/whoop-api

Contains:
- OAuth examples
- Client wrappers
- Data export scripts
- Dashboard integrations

Recommended usage:
- Reference implementations
- Testing endpoints
- Rapid prototyping

---

## Recommended Research Workflow

| Step | Tool |
|----|----|
User authorization | WHOOP OAuth |
Data retrieval | Official API |
Storage | Local database (SQLite/PostgreSQL) |
Analysis | Python / R |
Visualization | Dashboard or Jupyter |

---

## Important Notes

- WHOOP is a subscription-based analytics platform
- Data is computed server-side
- Sampling frequency is not exposed
- Suitable for longitudinal behavioral research
- Not suitable for raw physiological signal processing

---

## Position in Wearable Research

WHOOP should be treated as:

> A physiological interpretation service rather than a sensor acquisition device

This distinguishes it from research-grade wearables that provide raw signals.
