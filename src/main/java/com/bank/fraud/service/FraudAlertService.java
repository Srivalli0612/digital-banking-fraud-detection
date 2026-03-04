package com.bank.fraud.service;

import com.bank.fraud.dto.FraudAlertStatsDTO;
import com.bank.fraud.model.RiskLevel;
import com.bank.fraud.repository.FraudResultRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

@Service
public class FraudAlertService {

    private final FraudResultRepository repository;

    public FraudAlertService(FraudResultRepository repository) {
        this.repository = repository;
    }

    public FraudAlertStatsDTO getStats() {

        long total = repository.count();
        long fraudCount = repository.countByFraudDetectedTrue();

        LocalDateTime startOfDay =
                LocalDateTime.now().toLocalDate().atStartOfDay();

        long todayCount =
                repository.countByEvaluatedAtBetween(
                        startOfDay,
                        LocalDateTime.now()
                );

        // -----------------------------
        // Risk Breakdown
        // -----------------------------
        List<Object[]> results =
                repository.countByRiskLevelGroup();

        Map<RiskLevel, Long> riskMap =
                new EnumMap<>(RiskLevel.class);

        // Initialize all risk levels with 0
        for (RiskLevel level : RiskLevel.values()) {
            riskMap.put(level, 0L);
        }

        for (Object[] row : results) {
            RiskLevel level = (RiskLevel) row[0];
            Long count = (Long) row[1];

            if (level != null) {
                riskMap.put(level, count);
            }
        }

        return new FraudAlertStatsDTO(
                total,
                fraudCount,
                todayCount,
                riskMap
        );
    }
}