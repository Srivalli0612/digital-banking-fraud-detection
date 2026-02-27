package com.bank.fraud.repository;

import com.bank.fraud.model.FraudRuleConfig;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface FraudRuleConfigRepository 
        extends JpaRepository<FraudRuleConfig, Long> {

    Optional<FraudRuleConfig> findByRuleName(String ruleName);
}