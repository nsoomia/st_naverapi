export interface AviationMonthly {
    연도: number;
    월: number;
    "여객_계(명)": number;
}

export interface AviationTarget {
    연도: number;
    월: number;
    도시_norm: string;
    "여객_계(명)": number;
}

export interface CityMetric {
    대상도시: string;
    평점: number;
    리뷰수: number;
    저평점: number;
}

export interface CompanionRating {
    동행: string;
    평점: number;
}

export interface LengthByRating {
    평점: number;
    리뷰길이: number;
}

export interface DashboardData {
    aviation_monthly: AviationMonthly[];
    aviation_target: AviationTarget[];
    city_metrics: CityMetric[];
    rating_distribution: Record<string, number>;
    companion_rating: CompanionRating[];
    age_distribution: Record<string, number>;
    length_by_rating: LengthByRating[];
    keywords: {
        긍정: string[];
        부정: string[];
    };
}
