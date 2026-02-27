package com.bank.fraud.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.data.annotation.CreatedDate;

@Entity
@Table(name = "fraud_results")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FraudResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transaction_id")
    private Transaction transaction;

    private Boolean fraudDetected;

    @Column(columnDefinition = "TEXT")
    private String ruleTriggered;

    @Column(precision = 5, scale = 4)
    private BigDecimal riskScore;

    @Enumerated(EnumType.STRING)
    private AlertPriority priority;

    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime evaluatedAt;
}