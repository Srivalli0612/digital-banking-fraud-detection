package com.bank.fraud.specification;

import com.bank.fraud.model.FraudResult;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDateTime;

public class FraudResultSpecification {

    public static Specification<FraudResult> hasRiskLevel(String riskLevel) {
        return (root, query, cb) ->
                cb.equal(root.get("riskLevel"), riskLevel);
    }

    public static Specification<FraudResult> hasRule(String rule) {
        return (root, query, cb) ->
                cb.like(root.get("ruleTriggered"), "%" + rule + "%");
    }

    public static Specification<FraudResult> dateBetween(
            LocalDateTime from,
            LocalDateTime to) {

        return (root, query, cb) ->
                cb.between(root.get("evaluatedAt"), from, to);
    }
}