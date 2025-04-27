import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/lib/auth';
import { db } from '@/app/lib/db';

export async function GET(request: Request) {
  try {
    // Get user session
    const session = await getServerSession(authOptions);
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '10');
    const status = searchParams.get('status') || 'all';
    const type = searchParams.get('type') || 'all';
    const dateFrom = searchParams.get('dateFrom') || '';
    const dateTo = searchParams.get('dateTo') || '';
    const searchTerm = searchParams.get('search') || '';
    const sortOrder = searchParams.get('sortOrder') || 'newest';
    
    // Build query filters
    const filters: any = {
      userId: session.user.id,
    };
    
    // Status filter
    if (status !== 'all') {
      filters.status = status;
    }
    
    // Type filter
    if (type !== 'all') {
      filters.type = type;
    }
    
    // Date range filter
    if (dateFrom) {
      filters.createdAt = {
        ...(filters.createdAt || {}),
        gte: new Date(dateFrom),
      };
    }
    
    if (dateTo) {
      filters.createdAt = {
        ...(filters.createdAt || {}),
        lte: new Date(dateTo),
      };
    }
    
    // Search term filter (search in recipient name, transaction ID, or notes)
    if (searchTerm) {
      filters.OR = [
        { recipient: { contains: searchTerm, mode: 'insensitive' } },
        { transactionId: { contains: searchTerm, mode: 'insensitive' } },
        { notes: { contains: searchTerm, mode: 'insensitive' } },
      ];
    }
    
    // Calculate pagination
    const skip = (page - 1) * pageSize;
    
    // Determine sort order
    let orderBy: any = {};
    switch (sortOrder) {
      case 'oldest':
        orderBy = { createdAt: 'asc' };
        break;
      case 'amount-high':
        orderBy = { amount: 'desc' };
        break;
      case 'amount-low':
        orderBy = { amount: 'asc' };
        break;
      case 'newest':
      default:
        orderBy = { createdAt: 'desc' };
        break;
    }
    
    // Fetch transactions with pagination
    const transactions = await db.transaction.findMany({
      where: filters,
      orderBy,
      skip,
      take: pageSize,
      include: {
        sourceAccount: {
          select: {
            country: true,
          },
        },
        destinationAccount: {
          select: {
            country: true,
            accountName: true,
          },
        },
      },
    });
    
    // Get total count for pagination
    const totalCount = await db.transaction.count({
      where: filters,
    });
    
    // Get transaction summary
    const summary = await getTransactionSummary(session.user.id);
    
    return NextResponse.json({
      transactions: transactions.map(tx => ({
        id: tx.id,
        date: tx.createdAt.toISOString(),
        amount: tx.amount,
        currency: tx.currency,
        status: tx.status,
        type: tx.type,
        sourceCountry: tx.sourceAccount?.country || 'Unknown',
        destinationCountry: tx.destinationAccount?.country || 'Unknown',
        paymentMethod: tx.paymentMethod,
        recipient: tx.destinationAccount?.accountName || tx.recipient || 'Unknown',
      })),
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(totalCount / pageSize),
        totalCount,
      },
      summary,
    });
  } catch (error) {
    console.error('Error fetching transactions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch transactions' },
      { status: 500 }
    );
  }
}

// Helper function to get transaction summary
async function getTransactionSummary(userId: string) {
  // Get counts by status
  const statusCounts = await db.transaction.groupBy({
    by: ['status'],
    where: { userId },
    _count: true,
  });
  
  // Get counts by type
  const typeCounts = await db.transaction.groupBy({
    by: ['type'],
    where: { userId },
    _count: true,
  });
  
  // Calculate total volume (sum of all transaction amounts)
  const volumeResult = await db.transaction.aggregate({
    where: { userId, status: 'completed' },
    _sum: { amount: true },
  });
  
  // Build summary object
  const summary = {
    total: 0,
    pending: 0,
    completed: 0,
    failed: 0,
    domesticCount: 0,
    internationalCount: 0,
    volume: volumeResult._sum.amount || 0,
  };
  
  // Populate status counts
  statusCounts.forEach((item) => {
    const status = item.status as keyof typeof summary;
    summary[status] = item._count;
    summary.total += item._count;
  });
  
  // Populate type counts
  typeCounts.forEach((item) => {
    if (item.type === 'domestic') {
      summary.domesticCount = item._count;
    } else if (item.type === 'international') {
      summary.internationalCount = item._count;
    }
  });
  
  return summary;
} 