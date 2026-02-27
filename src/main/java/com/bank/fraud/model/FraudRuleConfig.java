package com.bank.fraud.model;

import java.math.BigDecimal;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "fraud_rule_config",
       indexes = @Index(name = "idx_rule_name", columnList = "ruleName"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FraudRuleConfig {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String ruleName;

    @Column(precision = 10, scale = 2)
    private BigDecimal thresholdValue;

    @Column(precision = 5, scale = 4)
    private BigDecimal weight;

    private Boolean active;
}