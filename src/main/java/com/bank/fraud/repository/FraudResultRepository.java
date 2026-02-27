package com.bank.fraud.repository;

import com.bank.fraud.model.AlertPriority;
import com.bank.fraud.model.FraudResult;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface FraudResultRepository extends
JpaRepository<FraudResult, Long>,
JpaSpecificationExecutor<FraudResult> {

long countByFraudDetected(Boolean fraudDetected);

List<FraudResult> findByPriority(AlertPriority priority);
}