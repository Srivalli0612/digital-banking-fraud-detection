package com.bank.fraud.specification;

import com.bank.fraud.model.Transaction;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDateTime;

public class TransactionSpecification {

    public static Specification<Transaction> hasFraudFlag(Boolean fraudFlag) {
        return (root, query, cb) ->
                fraudFlag == null ? null :
                        cb.equal(root.get("fraudFlag"), fraudFlag);
    }

    public static Specification<Transaction> hasSender(String sender) {
        return (root, query, cb) ->
                sender == null ? null :
                        cb.equal(root.get("senderAccountNumber"), sender);
    }

    public static Specification<Transaction> betweenDates(
            LocalDateTime start,
            LocalDateTime end) {

        return (root, query, cb) -> {
            if (start == null || end == null) return null;
            return cb.between(root.get("transactionTime"), start, end);
        };
    }
}