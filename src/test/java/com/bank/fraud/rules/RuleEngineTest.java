package com.bank.fraud.rules;

import com.bank.fraud.model.*;
import com.bank.fraud.service.FraudRuleConfigService;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class RuleEngineTest {

    private RuleEngine ruleEngine;
    private FraudRuleConfigService configService;

    @BeforeEach
    void setup() {

        configService = mock(FraudRuleConfigService.class);

        // -------------------------------
        // Mock active rule config
        // -------------------------------
        FraudRuleConfig activeRuleConfig = new FraudRuleConfig();
        activeRuleConfig.setActive(true);
        activeRuleConfig.setWeight(BigDecimal.ONE);
        activeRuleConfig.setThresholdValue(new BigDecimal("100000"));

        when(configService.getByRuleName(anyString()))
                .thenReturn(activeRuleConfig);

        // -------------------------------
        // Create rules list
        // -------------------------------
        List<FraudRule> rules = List.of(
                new HighAmountRule(configService),
                new ForeignLocationRule(configService),
                new SelfTransferRule(configService),
                new SuspiciousIPRule(configService),
                new SuspiciousMerchantRule(configService),
                new OddHoursRule(configService)
        );

        ruleEngine = new RuleEngine(rules);
    }

    // ---------------------------------------
    // Base Transaction (Normal)
    // ---------------------------------------
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

    // ---------------------------------------
    // HIGH AMOUNT
    // ---------------------------------------
    @Test
    void shouldTriggerHighAmountRule() {

        Transaction tx = baseTransaction();
        tx.setAmount(new BigDecimal("500000"));

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getNormalizedScore()
                .compareTo(BigDecimal.ZERO) > 0);

        assertTrue(result.getTriggeredRules()
                .contains("HIGH_AMOUNT_RULE"));
    }

    // ---------------------------------------
    // FOREIGN LOCATION
    // ---------------------------------------
    @Test
    void shouldTriggerForeignLocationRule() {

        Transaction tx = baseTransaction();
        tx.setLocation("USA");

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getTriggeredRules()
                .contains("FOREIGN_LOCATION_RULE"));
    }

    // ---------------------------------------
    // SELF TRANSFER
    // ---------------------------------------
    @Test
    void shouldTriggerSelfTransferRule() {

        Transaction tx = baseTransaction();
        tx.setReceiverAccountNumber("ACC1");

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getTriggeredRules()
                .contains("SELF_TRANSFER_RULE"));
    }

    // ---------------------------------------
    // SUSPICIOUS IP
    // ---------------------------------------
    @Test
    void shouldTriggerSuspiciousIPRule() {

        Transaction tx = baseTransaction();
        tx.setIpAddress("10.0.0.66");

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getTriggeredRules()
                .contains("SUSPICIOUS_IP_RULE"));
    }

    // ---------------------------------------
    // SUSPICIOUS MERCHANT
    // ---------------------------------------
    @Test
    void shouldTriggerSuspiciousMerchantRule() {

        Transaction tx = baseTransaction();
        tx.setMerchant("SCAM_PAY");

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getTriggeredRules()
                .contains("SUSPICIOUS_MERCHANT_RULE"));
    }

    // ---------------------------------------
    // ODD HOURS
    // ---------------------------------------
    @Test
    void shouldTriggerOddHoursRule() {

        Transaction tx = baseTransaction();
        tx.setTransactionTime(LocalDateTime.now().withHour(2));

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertTrue(result.getTriggeredRules()
                .contains("ODD_HOURS_RULE"));
    }

    // ---------------------------------------
    // NORMAL TRANSACTION
    // ---------------------------------------
    @Test
    void shouldNotTriggerFraudForNormalTransaction() {

        Transaction tx = baseTransaction();

        RuleEvaluationResult result = ruleEngine.evaluate(tx);

        assertEquals(BigDecimal.ZERO.setScale(4),
                result.getNormalizedScore());

        assertTrue(result.getTriggeredRules().isEmpty());
    }
}