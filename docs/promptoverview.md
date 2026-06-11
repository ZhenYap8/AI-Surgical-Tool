# AI Surgical Training Tool — Overview Document

**Project:** Surgical Training Risk Assessment Tool  
**Author:** Zhen Wei Yap  
**Status:** Trial / Pilot Phase  
**Last Updated:** 2025  

---

## Overview

This document describes the system architecture and input model for the AI-powered Surgical Training Risk Assessment Tool. The system predicts operative duration and overrun risk for surgical training cases, supporting theatre scheduling and trainee performance insight.

The system is composed of three functional layers:

| Layer | Name | Purpose |
|-------|------|---------|
| 1 | Prediction Engine | Estimates procedural duration distributions (P50, P80, P90) |
| 2 | Risk Classification | Assigns a traffic-light risk score (Green / Amber / Red) |
| 3 | Feedback Loop | Recalibrates model weights using actual vs. predicted outcomes |