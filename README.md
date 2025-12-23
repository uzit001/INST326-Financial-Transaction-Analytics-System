# INST326-TeamProject1

Team Members: 


# Domain Focus/Problem Statement

# Installation/Setup Instructions
# Usage Examples for Key Functions 

# Function Libary Overview/Organization
# Contribution Guidelines for Team Members

# Overview
Course: INST326 - Object-Oriented Programming for Information Science
Institution: University of Maryland, College Park
Semester: Fall 2024
Team: Uzzam Tariq, Keven Day, Kevin Miele, Angelo Montagnino

- The Problem:
People struggle to track their financial decisions and understand where their money is going. Small recurring charges like subscriptions can add up without them realizing.

- Our Solution:
A Python application that:
Tracks transactions across multiple account types
Imports data from bank CSV/JSON exports
Provides insights on spending patterns
Persists data between sessions
Generates detailed financial reports

- Key Questions Answered:
"How much money is in my account?"
"Which account has the most money?"
"What transactions have I made recently?"
"Where is my money coming from?"
"Where is my money going?"

# Features
- Multi-Account Management

Checking Accounts: Overdraft protection, check writing, monthly fees
Savings Accounts: Interest calculation, withdrawal limits (6/month federal regulation)
Credit Card Accounts: Credit limits, interest charges, rewards tracking

- Data Analytics

Category-based spending analysis
Recurring payment detection (subscriptions)
Spending trend identification
Monthly financial summaries
Budget vs. actual comparison

- Data Persistence

Save/Load: JSON-based system state persistence
Import: CSV and JSON transaction imports from banks
Export: CSV reports, JSON summaries, HTML monthly reports

- Data Quality

Comprehensive validation framework (amounts, dates, categories)
Automated data cleaning (duplicates, standardization)
Error handling for corrupted/missing data
98% data accuracy rate

- Testing & Reliability

30 Unit Tests: Individual component verification
8 Integration Tests: Cross-component coordination
5 System Tests: End-to-end workflow validation
95% Code Coverage: Comprehensive test suite
