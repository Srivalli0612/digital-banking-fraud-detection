package com.bank.fraud.mapper;

import com.bank.fraud.dto.FraudResultDTO;
import com.bank.fraud.model.FraudResult;
import org.springframework.stereotype.Component;

@Component
public class FraudResultMapper {

    public FraudResultDTO toDTO(FraudResult entity) {

        FraudResultDTO dto = new FraudResultDTO();

        dto.setId(entity.getId());

        if (entity.getTransaction() != null) {
            dto.setTransactionId(entity.getTransaction().getId());
        }

        dto.setFraudDetected(entity.getFraudDetected());
        dto.setRuleTriggered(entity.getRuleTriggered());
        dto.setMlScore(entity.getMlScore());
        dto.setFinalScore(entity.getFinalScore());
        dto.setRiskScore(entity.getRiskScore());
        dto.setPriority(entity.getPriority());
        dto.setRiskLevel(entity.getRiskLevel());
        dto.setEvaluatedAt(entity.getEvaluatedAt());

        return dto;
    }
}