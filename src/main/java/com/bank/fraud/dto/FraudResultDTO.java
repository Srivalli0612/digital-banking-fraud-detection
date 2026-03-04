package com.bank.fraud.dto;

import com.bank.fraud.model.Account;
import com.bank.fraud.model.AlertPriority;
import com.bank.fraud.model.RiskLevel;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.model.TransactionStatus;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FraudResultDTO { 

    private Long id;
    private Long transactionId;
    private Boolean fraudDetected;
    private String ruleTriggered;
    private BigDecimal mlScore;
    private BigDecimal finalScore;
    private BigDecimal riskScore;
    private AlertPriority priority;
    private RiskLevel riskLevel;
    private LocalDateTime evaluatedAt;

}