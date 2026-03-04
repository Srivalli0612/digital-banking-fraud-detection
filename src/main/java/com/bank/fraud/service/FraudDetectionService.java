package com.bank.fraud.service;

import com.bank.fraud.dto.FraudResultDTO;
import com.bank.fraud.dto.TransactionRequestDTO;
import com.bank.fraud.dto.TransactionResponseDTO;
import com.bank.fraud.model.Account;
import com.bank.fraud.model.AlertPriority;
import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.RiskLevel;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.model.TransactionStatus;
import com.bank.fraud.repository.AccountRepository;
import com.bank.fraud.repository.FraudResultRepository;
import com.bank.fraud.specification.FraudResultSpecification;

import jakarta.transaction.Transactional;

import com.bank.fraud.exception.AccountNotFoundException;
import com.bank.fraud.exception.InsufficientBalanceException;
import com.bank.fraud.mapper.FraudResultMapper;
import com.bank.fraud.repository.TransactionRepository;
import com.bank.fraud.rules.RuleEngine;
import com.bank.fraud.rules.RuleEvaluationResult;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class FraudDetectionService {

    private final FraudResultRepository fraudResultRepository;
    private final TransactionRepository transactionRepository;
    private final RuleEngine ruleEngine;          // now using RuleEngine
    private final RestTemplate restTemplate;
    private final FraudResultMapper fraudResultMapper;

    private static final Logger log = LoggerFactory.getLogger(FraudDetectionService.class);

    @Autowired
    private AccountRepository accountRepository;

    public FraudDetectionService(TransactionRepository transactionRepository,
                                 FraudResultRepository fraudResultRepository,
                                 RuleEngine ruleEngine,
                                 RestTemplate restTemplate,FraudResultMapper mapper) {
        this.transactionRepository = transactionRepository;
        this.fraudResultRepository = fraudResultRepository;
        this.ruleEngine = ruleEngine;
        this.restTemplate = restTemplate;
        this.fraudResultMapper = mapper; 
    }

    public Page<FraudResultDTO> getAlerts(String riskLevel, String rule, LocalDateTime from, LocalDateTime to, Pageable pageable) {
        Specification<FraudResult> spec = Specification.where(null);
        if (riskLevel != null && !riskLevel.isEmpty()) {
            spec = spec.and(FraudResultSpecification.hasRiskLevel(riskLevel));
        }
        if (rule != null && !rule.isEmpty()) {
            spec = spec.and(FraudResultSpecification.hasRule(rule));
        }
        if (from != null && to != null) {
            spec = spec.and(FraudResultSpecification.dateBetween(from, to));
        }
        
        Page<FraudResult> result = fraudResultRepository.findAll(spec, pageable);
        return result.map(fraudResultMapper::toDTO);
    }

    public FraudResult getByTransactionId(Long transactionId) {
        return fraudResultRepository.findByTransactionId(transactionId);
    }

    @Transactional
    public TransactionResponseDTO processTransaction(TransactionRequestDTO dto) {

        log.info("Processing transaction: {}", dto.getTransactionId());
        log.info("Fetching account: {}", dto.getSenderAccountNumber());

        Account account = accountRepository
                .findByAccountNumber(dto.getSenderAccountNumber())
                .orElseThrow(() -> {
                    log.error("Account not found: {}", dto.getSenderAccountNumber());
                    return new AccountNotFoundException("Account not found with number: " + dto.getSenderAccountNumber());
                });

        // Check sufficient balance
        if (account.getBalance().compareTo(dto.getAmount()) < 0) {
            throw new InsufficientBalanceException("Insufficient balance in account: " + dto.getSenderAccountNumber());
        }

        Transaction transaction = new Transaction();
        transaction.setTransactionId(dto.getTransactionId());
        transaction.setAccount(account);
        transaction.setAmount(dto.getAmount());
        transaction.setTransactionType(dto.getTransactionType());
        transaction.setLocation(dto.getLocation());
        transaction.setDeviceId(dto.getDeviceId());
        transaction.setMerchant(dto.getMerchant());
        transaction.setSenderName(dto.getSenderName());
        transaction.setReceiverName(dto.getReceiverName());
        transaction.setSenderAccountNumber(dto.getSenderAccountNumber());
        transaction.setReceiverAccountNumber(dto.getReceiverAccountNumber());
        transaction.setIpAddress(dto.getIpAddress());
        transaction.setStatus(TransactionStatus.valueOf(dto.getStatus()));

//        transaction.setTransactionTime(
//                dto.getTransactionTime() != null ? dto.getTransactionTime() : LocalDateTime.now()
//        );

        // Update and save account balance
        account.withdrawlMoney(dto.getAmount());
        accountRepository.save(account);

        Transaction savedTx = transactionRepository.save(transaction);
        log.info("Transaction saved with ID: {}", savedTx.getTransactionId());

        // ==========================================
        // 1. Get Rule-Based Engine Score (0-1)
        // ==========================================
        RuleEvaluationResult ruleResult =
                ruleEngine.evaluate(savedTx);

        BigDecimal ruleScore = ruleResult.getNormalizedScore();
        String triggeredRules = ruleResult.getTriggeredRules();

        
//        // ==========================================
//        // 2. Get ML Model Score (Python API Call)
//        // ==========================================
//        BigDecimal mlScore = getMLFraudProbability(savedTx);
//
//        // ==========================================
//        // 3. Weights
//        // ==========================================
//        BigDecimal ruleWeight = new BigDecimal("0.6");
//        BigDecimal mlWeight = new BigDecimal("0.4");
//        // Final HYBRID FRAUD SCORE
//        BigDecimal finalScore = ruleScore.multiply(ruleWeight)
//                .add(mlScore.multiply(mlWeight))
//                .setScale(4, RoundingMode.HALF_UP);;
        
        

        // ==========================================
        // 4. Determine risk level
        // ==========================================
        RiskLevel riskLevel = calculateRiskLevel(ruleScore);
        
        //Fraud Decision or fraud flag
        boolean isFraud = riskLevel == RiskLevel.HIGH_RISK
                || riskLevel == RiskLevel.CRITICAL_RISK;

        // Map riskLevel to priority
        AlertPriority priority = mapPriority(riskLevel);

//        log.info("Hybrid Evaluation -> Rule Score: {}, ML Score: {}, Final Score: {}, Risk: {}",
//                ruleScore, mlScore, finalScore, riskLevel);

        // ==========================================
        // 5. Update Transaction with fraud flag
        // ==========================================
        savedTx.setFraudFlag(isFraud);
        transactionRepository.save(savedTx);

        // ==========================================
        // 6. Create and save final FraudResult
        // ==========================================
        FraudResult finalResult = new FraudResult();
        finalResult.setFraudDetected(isFraud);
        finalResult.setRiskLevel(riskLevel);
        finalResult.setTransaction(savedTx);
//        finalResult.setMlScore(mlScore);
//        finalResult.setFinalScore(finalScore);
//        finalResult.setRiskScore(finalScore); // store as 0-1 (or convert to percentage if needed)
        finalResult.setRiskScore(ruleScore);// temporarly added
        finalResult.setPriority(priority);
        finalResult.setRuleTriggered(triggeredRules); // keep triggered rules from rule engine

        fraudResultRepository.save(finalResult);

        // ==========================================
        // 7. Build the Response DTO
        // ==========================================
        TransactionResponseDTO response = new TransactionResponseDTO();
        response.setTransactionId(savedTx.getTransactionId());
        response.setAmount(savedTx.getAmount());
        response.setFraudDetected(isFraud);
        response.setRuleTriggered(finalResult.getRuleTriggered());
        // If the DTO expects a percentage (0-100), convert it:
//        BigDecimal scorePercentage = finalScore.multiply(new BigDecimal("100"))
//                .setScale(2, RoundingMode.HALF_UP);
//        response.setRiskScore(scorePercentage);
        response.setRiskScore(ruleScore);// temporarly added
        response.setTransactionTime(savedTx.getTransactionTime());

        return response;
    }

    /**
     * Maps a numeric score (0-1) to a RiskLevel.
     */
    private RiskLevel calculateRiskLevel(BigDecimal score) {
        if (score.compareTo(new BigDecimal("0.3")) < 0) {
            return RiskLevel.LOW_RISK;
        } else if (score.compareTo(new BigDecimal("0.6")) < 0) {
            return RiskLevel.MEDIUM_RISK;
        } else if (score.compareTo(new BigDecimal("0.8")) < 0) {
            return RiskLevel.HIGH_RISK;
        } else {
            return RiskLevel.CRITICAL_RISK;
        }
    }

    /**
     * Maps a RiskLevel to an AlertPriority.
     */
    private AlertPriority mapPriority(RiskLevel level) {
        switch (level) {
            case LOW_RISK:
                return AlertPriority.LOW;
            case MEDIUM_RISK:
                return AlertPriority.MEDIUM;
            case HIGH_RISK:
                return AlertPriority.HIGH;
            case CRITICAL_RISK:
                return AlertPriority.CRITICAL;
            default:
                return AlertPriority.LOW;
        }
    }

    /**
     * Calls the Python FastAPI ML Model and returns a fraud probability as BigDecimal (0-1).
     */
    private BigDecimal getMLFraudProbability(Transaction transaction) {
        String mlApiUrl = "http://localhost:8000/predict";

        Map<String, Object> mlRequest = new HashMap<>();
        mlRequest.put("amount", transaction.getAmount());
        mlRequest.put("hour", transaction.getTransactionTime().getHour());
        // Dummy features – replace with real data in production
        mlRequest.put("locationRisk", new BigDecimal("5.0"));
        mlRequest.put("velocityScore", new BigDecimal("2.0"));

        try {
            Map<String, Object> response = restTemplate.postForObject(mlApiUrl, mlRequest, Map.class);
            if (response != null && response.containsKey("fraudProbability")) {
                return new BigDecimal(response.get("fraudProbability").toString());
            }
        } catch (Exception e) {
            log.error("Failed to connect to ML Engine at {}. Defaulting ML score to 0.0", mlApiUrl, e);
        }
        return BigDecimal.ZERO; // fallback
    }
}