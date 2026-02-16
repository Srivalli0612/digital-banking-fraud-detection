package com.bank.fraud.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "fraud_results")
public class FraudResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    private Transaction transaction;

    private Boolean fraudDetected;

    private String ruleTriggered;

    private Double riskScore; // ML or rule score

    private LocalDateTime evaluatedAt;

    // -------- Constructors --------
    public FraudResult() {
        this.evaluatedAt = LocalDateTime.now();
    }

    // -------- Getters & Setters --------
    public Long getId() {
        return id;
    }

    public Transaction getTransaction() {
        return transaction;
    }

    public void setTransaction(Transaction transaction) {
        this.transaction = transaction;
    }

    public Boolean getFraudDetected() {
        return fraudDetected;
    }

    public void setFraudDetected(Boolean fraudDetected) {
        this.fraudDetected = fraudDetected;
    }

    public String getRuleTriggered() {
        return ruleTriggered;
    }

    public void setRuleTriggered(String ruleTriggered) {
        this.ruleTriggered = ruleTriggered;
    }

    public Double getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(Double riskScore) {
        this.riskScore = riskScore;
    }

    public LocalDateTime getEvaluatedAt() {
        return evaluatedAt;
    }
}
