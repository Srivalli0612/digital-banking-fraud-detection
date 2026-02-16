package com.bank.fraud.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import com.bank.fraud.model.Transaction;

public interface TransactionRepository extends JpaRepository<Transaction, Long> {
	List<Transaction> findByAccountIdAndTransactionTimeAfter(
            Long accountId,
            LocalDateTime time
    );
}
