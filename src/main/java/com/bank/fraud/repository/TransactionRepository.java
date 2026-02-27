package com.bank.fraud.repository;

import com.bank.fraud.model.Transaction;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface TransactionRepository extends
        JpaRepository<Transaction, Long>,
        JpaSpecificationExecutor<Transaction> {

    // 🔹 Pagination support
    Page<Transaction> findByFraudFlag(Boolean fraudFlag, Pageable pageable);

    Page<Transaction> findBySenderAccountNumber(
            String senderAccountNumber,
            Pageable pageable);

    // 🔹 Time-based search
    List<Transaction> findBySenderAccountNumberAndTransactionTimeAfter(
            String senderAccountNumber,
            LocalDateTime time);

    // 🔹 Fraud dashboard count
    long countByFraudFlag(Boolean fraudFlag);

    // 🔹 Failed attempts count
    @Query("""
    	       SELECT COUNT(t)
    	       FROM Transaction t
    	       WHERE t.senderAccountNumber = :sender
    	       AND t.transactionTime >= :time
    	       """)
    	long countRecentTransactions(
    	        @Param("sender") String sender,
    	        @Param("time") LocalDateTime time
    	);
    
    
    
    @Query("""
    	       SELECT COUNT(t)
    	       FROM Transaction t
    	       WHERE t.senderAccountNumber = :sender
    	       AND t.status = 'FAILED'
    	       AND t.transactionTime >= :time
    	       """)
    	long countRecentFailedTransactions(
    	        @Param("sender") String sender,
    	        @Param("time") LocalDateTime time
    	);
    
}