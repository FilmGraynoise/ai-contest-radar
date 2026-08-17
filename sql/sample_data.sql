insert into public.contests (
  fingerprint, title, organizer, deadline, prize_text, total_prize_won,
  eligibility, categories, ai_requirement, ai_reason, ai_confidence,
  summary, source, source_url
)
values
(
  'sample-ai-video-001',
  '[샘플] 생성형 AI 숏폼 영상 공모전',
  '샘플 주최사',
  current_date + 21,
  '총상금 1,000만원',
  10000000,
  '대한민국 국민 누구나',
  array['video'],
  'required',
  '공고에서 생성형 AI를 활용한 영상 제작을 필수 조건으로 명시한 샘플입니다.',
  0.99,
  '생성형 AI를 활용해 60초 이내 숏폼 영상을 제작하는 샘플 공모전입니다. 실제 데이터가 아닙니다.',
  'sample',
  'https://example.com'
)
on conflict (fingerprint) do nothing;
