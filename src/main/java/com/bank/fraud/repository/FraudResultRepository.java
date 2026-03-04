package com.bank.fraud.repository;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.RiskLevel;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;

public interface FraudResultRepository
        extends JpaRepository<FraudResult, Long>,
                JpaSpecificationExecutor<FraudResult> {

    FraudResult findByTransactionId(Long transactionId);
    
    long countByFraudDetectedTrue();

    long countByRiskLevel(RiskLevel riskLevel);

    long countByEvaluatedAtBetween(
            LocalDateTime start,
            LocalDateTime end
    );
    
    @Query("""
    	       SELECT f.riskLevel, COUNT(f)
    	       FROM FraudResult f
    	       WHERE f.riskLevel IS NOT NULL
    	       GROUP BY f.riskLevel
    	       """)
    	List<Object[]> countByRiskLevelGroup();
}