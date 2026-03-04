package com.bank.fraud.dto;

import java.util.Map;

import com.bank.fraud.model.RiskLevel;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class FraudAlertStatsDTO {

    private long totalAlerts;
    private long fraudCount;
    private long todayAlerts;
    
    private Map<RiskLevel, Long> riskBreakdown;
} 