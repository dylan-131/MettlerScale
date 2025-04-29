# Project Scope: Automated Integration of Mettler Toledo ICS435 with Tempo MES

## Overview

This project aims to automate the data acquisition process from a Mettler Toledo ICS435 scale and integrate the live weight data into a Tempo MES procedure. The goal is to create a robust demo that showcases real-time scale integration within a digital manufacturing workflow. This will eventually be used to drive more advanced use cases, including wearable device integration (e.g., RealWear) and smart approvals.

## Objectives

- Establish a live connection to the ICS435 scale via Ethernet.
- Capture weight data in real-time and forward it to the Tempo MES system.
- Automate decision-making within the Tempo procedure based on scale output (e.g., pass/fail weight ranges).
- Build a reusable and scalable setup that can later be expanded to other devices or platforms.

## Current Stage

At this point in the project, the ICS435 scale is physically connected to an in houce PC via Ethernet, and the IP address has been detected (currently assigned dynamically via DHCP). The primary hurdle is determining the correct communication port and protocol the scale uses, in order to receive weight readings programmatically.

## Role of the Detection Script

The current script plays a critical role in the integration workflow:

- **Ping Discovery:** Confirms the scale's presence on the subnet and logs the assigned IP address.
- **Port Scanning:** Attempts to identify which ports the scale has open to understand how to establish a connection (e.g., raw TCP, HTTP, etc.).
- **Communication Testing:** Lays the groundwork for the actual data pull from the scale by validating connectivity.

Without identifying the correct network port and communication method, it is not possible to capture live weight data, rendering the rest of the integration non-functional. This script, therefore, serves as the gateway to unlocking the full data pipeline between the scale and the Tempo MES.

## Next Steps

- Receive clarification from Mettler Toledo on port/protocol configuration.
- Confirm if static IP can be set for consistent access.
- Establish a working connection and test live data capture.
- Integrate script into an AWS Lambda function for automation (optional future step).
- Embed scale data capture and logic into the Tempo procedure.

## Long-Term Vision

This script and integration are part of a larger vision to demonstrate a modular, sensor-integrated smart manufacturing environment. The learnings from this project will inform future deployments, including other OT devices, real-time dashboards, and voice-guided operator assistance through wearables.