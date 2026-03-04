package com.bank.fraud.model;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions",
       indexes = {
           @Index(name = "idx_sender_account", columnList = "senderAccountNumber"),
           @Index(name = "idx_transaction_time", columnList = "transactionTime"),
           @Index(name = "idx_fraud_flag", columnList = "fraudFlag")
       })
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String transactionId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "account_id", nullable = false)
    private Account account;

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false)
    private String transactionType;

    @Column(nullable = false)
    private String location;

    @Column(nullable = false)
    private String deviceId;

    @Column(nullable = false)
    private String merchant;
    
    @Column(nullable = false)
    private String senderName;
    
    @Column(nullable = false)
    private String receiverName;

    @Column(nullable = false)
    private String senderAccountNumber;

    @Column(nullable = false)
    private String receiverAccountNumber;

    @Column(nullable = false)
    private String ipAddress;

    @Enumerated(EnumType.STRING)
    private TransactionStatus status;

    @Column(nullable = false)
    private Boolean fraudFlag = false;

    @Column(nullable = false)
    @CreatedDate
    private LocalDateTime transactionTime;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @Version
    private Long version = 0L;
}