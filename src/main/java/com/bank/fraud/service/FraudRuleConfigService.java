package com.bank.fraud.service;

import com.bank.fraud.model.FraudRuleConfig;
import com.bank.fraud.repository.FraudRuleConfigRepository;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class FraudRuleConfigService {

    private final FraudRuleConfigRepository repository;

    public FraudRuleConfigService(FraudRuleConfigRepository repository) {
        this.repository = repository;
    }

    @Cacheable(value = "ruleConfigs", key = "#ruleName")
    public FraudRuleConfig getByRuleName(String ruleName) {
        return repository.findByRuleName(ruleName)
                .orElse(null);
    }
}