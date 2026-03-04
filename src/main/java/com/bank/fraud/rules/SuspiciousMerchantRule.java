package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Component;

@Component
public class SuspiciousMerchantRule extends BaseRule {

    private static final List<String> BLACKLIST =
            List.of("SCAM_PAY", "DARKWEB_STORE", "ILLEGAL_SHOP");

    public SuspiciousMerchantRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        String merchant = transaction.getMerchant();

        if (merchant != null &&
                BLACKLIST.contains(merchant.toUpperCase())) {

            return riskScore();   // return configured rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "SUSPICIOUS_MERCHANT_RULE";
    }
}