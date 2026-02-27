package com.bank.fraud.service;

import com.bank.fraud.dto.TransactionResponseDTO;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.specification.TransactionSpecification;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class TransactionService {

    private final TransactionRepository transactionRepository;

    public Page<TransactionResponseDTO> getTransactions(
            Boolean fraudFlag,
            String senderAccount,
            int page,
            int size,
            String sortBy,
            String direction
    ) {

        log.info("Fetching transactions with filters");

        Sort sort = direction.equalsIgnoreCase("desc")
                ? Sort.by(sortBy).descending()
                : Sort.by(sortBy).ascending();

        Pageable pageable = PageRequest.of(page, size, sort);

        Specification<Transaction> spec =
                Specification.where(TransactionSpecification.hasFraudFlag(fraudFlag))
                        .and(TransactionSpecification.hasSender(senderAccount));

        Page<Transaction> transactionPage =
                transactionRepository.findAll(spec, pageable);

        return transactionPage.map(this::mapToDTO);
    }

    private TransactionResponseDTO mapToDTO(Transaction tx) {
        TransactionResponseDTO dto = new TransactionResponseDTO();
        dto.setTransactionId(tx.getTransactionId());
        dto.setFraudDetected(tx.getFraudFlag());
        dto.setRiskScore(null); // optional if linking FraudResult
        dto.setTransactionTime(tx.getTransactionTime());
        return dto;
    }
}