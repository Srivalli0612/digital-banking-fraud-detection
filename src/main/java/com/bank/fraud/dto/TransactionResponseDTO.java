package com.bank.fraud.dto;

import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TransactionResponseDTO {
 
    private String transactionId;
    private BigDecimal amount;
    private Boolean fraudDetected;
    private String ruleTriggered;
    private BigDecimal riskScore;
    private LocalDateTime transactionTime;
}