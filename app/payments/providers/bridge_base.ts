export interface BridgeResult {
  tx_id: string;
  status: string;
  settled_at: Date;
}

export interface BridgeProvider {
  onramp(
    amount: number,
    currency: string,
    srcChain: string | number,
    dstChain: string | number,
    recipient: string
  ): Promise<BridgeResult>;
  
  offramp(
    amount: number,
    currency: string,
    chain: string | number,
    bankAccountId: string
  ): Promise<BridgeResult>;
} 