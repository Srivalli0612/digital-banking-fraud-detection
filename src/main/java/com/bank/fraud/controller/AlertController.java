package com.bank.fraud.controller;

import com.bank.fraud.dto.FraudAlertStatsDTO;
import com.bank.fraud.dto.FraudResultDTO;
import com.bank.fraud.model.FraudResult;
import com.bank.fraud.service.FraudAlertService;
import com.bank.fraud.service.FraudDetectionService;
import org.springframework.data.domain.*;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;

@RestController
@RequestMapping("/api/v1/alerts")
public class AlertController { 

    private final FraudDetectionService fraudDetectionService;
    private final FraudAlertService fraudAlertService;
    
    public AlertController(FraudDetectionService fraudDetectionService, 
    		FraudAlertService fraudAlertService) {
        this.fraudDetectionService = fraudDetectionService;
        this.fraudAlertService = fraudAlertService;
    }

    /**
     * GET All Alerts with Filtering + Pagination
     */
    @GetMapping
    public ResponseEntity<Page<FraudResultDTO>> getAlerts(
            @RequestParam(required = false) String riskLevel,
            @RequestParam(required = false) String rule,
            @RequestParam(required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
            LocalDateTime from,

            @RequestParam(required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
            LocalDateTime to,

            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "evaluatedAt") String sortBy,
            @RequestParam(defaultValue = "desc") String direction
    ) {

        Sort sort = direction.equalsIgnoreCase("asc") ?
                Sort.by(sortBy).ascending() :
                Sort.by(sortBy).descending();

        Pageable pageable = PageRequest.of(page, size, sort);

        Page<FraudResultDTO> result =
                fraudDetectionService.getAlerts(
                        riskLevel,
                        rule,
                        from,
                        to,
                        pageable
                );

        return ResponseEntity.ok(result);
    }

    /**
     * GET High Risk Alerts
     */
    @GetMapping("/high-risk")
    public ResponseEntity<Page<FraudResultDTO>> getHighRiskAlerts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable =
                PageRequest.of(page, size, Sort.by("evaluatedAt").descending());

        Page<FraudResultDTO> result =
                fraudDetectionService.getAlerts(
                        "HIGH",
                        null,
                        null,
                        null,
                        pageable
                );

        return ResponseEntity.ok(result);
    }

    /**
     * GET Alerts by Rule
     */
    @GetMapping("/by-rule/{ruleName}")
    public ResponseEntity<Page<FraudResultDTO>> getAlertsByRule(
            @PathVariable String ruleName,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable =
                PageRequest.of(page, size, Sort.by("evaluatedAt").descending());

        Page<FraudResultDTO> result =
                fraudDetectionService.getAlerts(
                        null,
                        ruleName,
                        null,
                        null,
                        pageable
                );

        return ResponseEntity.ok(result);
    }

    /**
     * GET Alert by Transaction ID
     */
    @GetMapping("/transaction/{transactionId}")
    public ResponseEntity<FraudResult> getByTransactionId(
            @PathVariable Long transactionId) {

        FraudResult result =
                fraudDetectionService.getByTransactionId(transactionId);

        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/stats")
    public ResponseEntity<FraudAlertStatsDTO> getDashboardStats() {
        return ResponseEntity.ok(fraudAlertService.getStats());
    }
}