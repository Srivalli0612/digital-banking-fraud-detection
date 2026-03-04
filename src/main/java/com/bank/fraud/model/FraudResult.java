package com.bank.fraud.model;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;


@Entity
@Table(name = "fraud_results")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EntityListeners(AuditingEntityListener.class)
public class FraudResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transaction_id")
    @JsonIgnore
    private Transaction transaction;

    private Boolean fraudDetected;

    @Column(columnDefinition = "TEXT")
    private String ruleTriggered;
    
 // ✅ NEW: Individual score from the Python ML Engine (0.0000 to 1.0000). What the AI thought.
    @Column(precision = 5, scale = 4)
    private BigDecimal mlScore; 

    // ✅ NEW: The raw weighted calculation result before scaling to 100. The result of (Rule * 0.6) + (ML * 0.4).
    @Column(precision = 5, scale = 4)
    private BigDecimal finalScore;

    // The user-friendly 0-100 percentage.
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