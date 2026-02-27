package com.bank.fraud.rules;

import com.bank.fraud.model.*;
import com.bank.fraud.repository.FraudRuleConfigRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class RuleEngineTest {

    private RuleEngine ruleEngine;
    private FraudRuleConfigRepository configRepository;

    @BeforeEach
    void setup() {

        configRepository = mock(FraudRuleConfigRepository.class);

        // Mock global threshold
        FraudRuleConfig config = new FraudRuleConfig();
        config.setThresholdValue(new BigDecimal("0.5"));

        when(configRepository.findByRuleName("GLOBAL_FRAUD_THRESHOLD"))
                .thenReturn(Optional.of(config));

        List<FraudRule> rules = List.of(
                new HighAmountRule(configRepository),
                new ForeignLocationRule(configRepository),
                new SelfTransferRule(configRepository),
                new SuspiciousIPRule(configRepository),
                new SuspiciousMerchantRule(configRepository),
                new OddHoursRule(configRepository)
        );

        ruleEngine = new RuleEngine(rules, configRepository);
    }

    private Transaction baseTransaction() {
        Transaction tx = new Transaction();
        tx.setAmount(new BigDecimal("1000"));
        tx.setLocation("INDIA");
        tx.setIpAddress("192.168.1.1");
        tx.setMerchant("AMAZON");
        tx.setSenderAccountNumber("ACC1");
        tx.setReceiverAccountNumber("ACC2");
        tx.setStatus(TransactionStatus.SUCCESS);
        tx.setTransactionTime(LocalDateTime.now().withHour(14));
        return tx;
    }

    // --------------------------------------------
    // HIGH AMOUNT RULE
    // --------------------------------------------

    @Test
    void shouldTriggerHighAmountRule() {

        Transaction tx = baseTransaction();
        tx.setAmount(new BigDecimal("500000"));

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getFraudDetected());
        assertTrue(result.getRuleTriggered().contains("HIGH_AMOUNT_RULE"));
    }

    // --------------------------------------------
    // FOREIGN LOCATION RULE
    // --------------------------------------------

    @Test
    void shouldTriggerForeignLocationRule() {

        Transaction tx = baseTransaction();
        tx.setLocation("USA");

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getRuleTriggered().contains("FOREIGN_LOCATION_RULE"));
    }

    // --------------------------------------------
    // SELF TRANSFER RULE
    // --------------------------------------------

    @Test
    void shouldTriggerSelfTransferRule() {

        Transaction tx = baseTransaction();
        tx.setReceiverAccountNumber("ACC1");

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getRuleTriggered().contains("SELF_TRANSFER_RULE"));
    }

    // --------------------------------------------
    // SUSPICIOUS IP RULE
    // --------------------------------------------

    @Test
    void shouldTriggerSuspiciousIPRule() {

        Transaction tx = baseTransaction();
        tx.setIpAddress("10.0.0.66");

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getRuleTriggered().contains("SUSPICIOUS_IP_RULE"));
    }

    // --------------------------------------------
    // SUSPICIOUS MERCHANT RULE
    // --------------------------------------------

    @Test
    void shouldTriggerSuspiciousMerchantRule() {

        Transaction tx = baseTransaction();
        tx.setMerchant("SCAM_PAY");

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getRuleTriggered().contains("SUSPICIOUS_MERCHANT_RULE"));
    }

    // --------------------------------------------
    // ODD HOURS RULE
    // --------------------------------------------

    @Test
    void shouldTriggerOddHoursRule() {

        Transaction tx = baseTransaction();
        tx.setTransactionTime(LocalDateTime.now().withHour(2));

        FraudResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getRuleTriggered().contains("ODD_HOURS_RULE"));
    }

    // --------------------------------------------
    // NORMAL TRANSACTION
    // --------------------------------------------

    @Test
    void shouldNotTriggerFraudForNormalTransaction() {

        Transaction tx = baseTransaction();

        FraudResult result = ruleEngine.evaluate(tx);

        assertFalse(result.getFraudDetected());
    }
}